#!/usr/bin/env python3

#import boto3
import os
import subprocess
import glob
from time import time
from datetime import datetime
from sqlalchemy.orm import Query
from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import albumentations as A
import cv2
import re
import logging
from celery.utils.log import get_task_logger
from torchvision import datasets
import torch
import torchvision
from torchvision import transforms as transforms
import gc

# Ubuntu fix for model download
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


Base = declarative_base()

DATA_FOLDER = '/home/andrei/Desktop/imachines/homework/fashion-dataset'
OUTPUT_FOLDER = '/home/andrei/Desktop/imachines/homework/out'
DB_URL = 'postgresql://postgres:postgres@localhost:5433/homework'


model_ft = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model_ft.to(0)
model_ft.eval()

class StyleImage(Base):
    """ Class representing image and known metadata in database"""
    
    __tablename__ = 'style_image'
    id = Column(Integer, primary_key=True, nullable=False) 
    file_id = Column(Integer)
    file_name = Column(String(255))
    url = Column(String(1000))
    gender = Column(String(255))
    masterCategory = Column(String(255))
    subCategory = Column(String(255))
    articleType = Column(String(255))
    baseColour = Column(String(255))
    season = Column(String(255))
    year = Column(Integer)
    usage = Column(String(255))
    productDisplayName = Column(String(255))


def _open_session(dbURL):
    """ Utility function for opening SQLAlchemy session """ 

    engine = create_engine(dbURL)

    if not database_exists(engine.url):
        create_database(engine.url)

    Base.metadata.create_all(bind=engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    return session()


def process_query(query, folder):
    """Function for processing SQLAlchemy query for StyleImage query and 
    saving results to the corresponding folder

    Params:
    query - SQLAlchemy Query
    folder - output folder
    """
    
    # ensure folders exist
    target_dir = os.path.join(OUTPUT_FOLDER, folder)
    target_images_dir = os.path.join(target_dir, 'images')
    target_styles_dir = os.path.join(target_dir, 'styles')
    try:
        os.makedirs(target_images_dir)
        os.makedirs(target_styles_dir)
    except FileExistsError:
        # directory already exists
        pass        

    s = _open_session(DB_URL)
    try:
        results = query.with_session(s)

        for item in results:
            source_image_path = os.path.join(DATA_FOLDER, 'images', item.file_name)
            source_json_path = os.path.join(DATA_FOLDER, 'styles', f'{item.file_id}.json')
            # subprocess.call(["cp", source_image_path, target_image_path],shell=True)
            
            os.system(f'cp {source_image_path} {target_images_dir}') 
            os.system(f'cp {source_json_path} {target_styles_dir}')
            
    finally:
        s.close()


def _augment_image(source_file, dest_dir, size=256):
    """ Utility function to augment one image """
    
    im = cv2.imread(source_file)
    aug = A.RandomResizedCrop(size, size, scale=(0.8, 0.8))
    augmented = aug(image=im)
    filename, file_extension = os.path.splitext(source_file) 
    basename = os.path.basename(filename)
    cv2.imwrite(os.path.join(dest_dir, basename+'_au'+file_extension), augmented['image'])


def list_folder(folder):
    """ Utility function for notebook to get resulting files separated by types """
    
    target_folder = os.path.join(OUTPUT_FOLDER, folder)
    if os.path.exists(target_folder):
        images = glob.glob(os.path.join(target_folder, 'images', "**"))
        augmented_images = glob.glob(os.path.join(target_folder, 'augmented_images', '**'))
        styles = glob.glob(os.path.join(target_folder, 'styles', '**'))
        images.sort()
        augmented_images.sort()
        styles.sort()
        return {'images':images, 'augmented_images':augmented_images, 'styles':styles}
    else:
        return None

def transform_folder(folder, size=256):
    """ Apply augmentations to images in the specified folder to apply specified size """

    dest_dir = os.path.join(OUTPUT_FOLDER, folder, 'augmented_images')
    try:
        os.makedirs(dest_dir)
    except FileExistsError:
        # directory already exists
        pass        

    original_images = list_folder(folder)
    for image_file in original_images['images']:
        _augment_image(image_file, dest_dir, size)


def clean_folder(folder):
    """ Remove experiment data """
    
    target_folder = os.path.join(OUTPUT_FOLDER, folder)
    subprocess.run(["rm", "-rf", target_folder])


def ingest(dbURL, root_dataset_path, use_celery_logger=True):
    """ Ingest dataset into specified database """

    if use_celery_logger:
        logger = get_task_logger(__name__)
    else:
        logger = logging.getLogger(__name__)

    t = time()

    s = _open_session(dbURL)

    try:
        # todo: set path as an argument
        images_file_name = os.path.join(root_dataset_path, 'images.csv') 
        styles_file_name = os.path.join(root_dataset_path, 'styles.csv') 

        # delete old data first as this is not an incremental update
        num_rows_deleted = s.query(StyleImage).delete()
        s.commit()
        logger.info(f'Old rows deleted: {num_rows_deleted}')

        
        # have to process files manually as styles file contains some lines with more delimiters then expected
        accepted_record_count = 0
        with open(images_file_name, 'r') as images_f, open(styles_file_name, 'r') as styles_f:
            line_num = 0
            # skip header
            images_f.readline()
            styles_f.readline()
            for image_line, style_line in zip(images_f, styles_f):
                line_num += 1
                image_values = image_line.split(',')
                style_values = style_line.split(',')
                # check line id match
                if not image_values[0].startswith(style_values[0]):
                    logger.info(f"Image file id {image_values[0]} doesn't correspond to style file id {style_values[0]} at line {line_num}")
                    continue
                
                # if style data has more columns then expected then last column should collect all the data
                if len(style_values) > 10:
                    style_values[9] = ','.join(style_values[9:])
                
                record = StyleImage(**{
                    'file_name' : image_values[0],
                    'url' : image_values[1],
                    'file_id': int(style_values[0]) if style_values[0].isdigit() else -1,
                    'gender': style_values[1],
                    'masterCategory': style_values[2],
                    'subCategory': style_values[3],
                    'articleType': style_values[4],
                    'baseColour': style_values[5],
                    'season': style_values[6],
                    'year': int(style_values[7]) if style_values[7].isdigit() else -1,
                    'usage': style_values[8],
                    'productDisplayName': style_values[9]

                })
                s.add(record) #Add all the records
                accepted_record_count += 1

            
            logger.info(f'Total collected records {accepted_record_count}')

        s.commit() #Attempt to commit all the records
    except Exception as e:
        logger.exception(e)
        s.rollback() #Rollback the changes on error
    finally:
        s.close() #Close the connection

    time_elapsed = time() - t
    logger.info(f'Time elapsed: {time_elapsed}')

    # checking amount of loaded recors
    inserted_rec_count = s.query(StyleImage).count()
    logger.info(f'Inserted records: {inserted_rec_count}')

    # checking how many year records weren't properly converted
    missing_year_count = s.query(StyleImage).filter(StyleImage.year == -1).count()
    logger.info(f'Records with missing year: {missing_year_count}')

    # checking how many id records weren't properly converted
    missing_id_count = s.query(StyleImage).filter(StyleImage.id == -1).count()
    logger.info(f'Records with missing id: {missing_id_count}')
    logger.info('Done!')


def predict_folder(folder):
    """ Get model predictions on augmented image set """
    
    device = 0
    data_transforms = transforms.ToTensor()

    image_folder = os.path.join(OUTPUT_FOLDER, folder)
    
    # filtering to predict only augmented images
    classes = ["augmented_images"]

    def __checkfun(args):
        return args.split("/")[-2] in classes and args.endswith(".jpg") 

    def __find_classes(self, dir):
        return classes, {c: i for i, c in enumerate(classes)}

    torchvision.datasets.ImageFolder._find_classes = __find_classes
    
    dataset = datasets.ImageFolder(image_folder, data_transforms, is_valid_file=__checkfun)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size = 1, shuffle=False, num_workers=1)

    outputs = []
    t = time()
    result = []
    for inputs, label in dataloader:
        inputs = inputs.to(device)
        output = model_ft(inputs)
        # transfer tensors from GPU to CPU
        prediction = {'boxes':output[0]['boxes'].to('cpu'),'labels':output[0]['labels'].to('cpu')}
        del output
        result.append(prediction)
    
    # clean memory for repetitive calls
    torch.cuda.empty_cache()
    gc.collect()

    time_elapsed = time() - t
    print(f'Time elapsed: {time_elapsed}')

    return result
