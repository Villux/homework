#!/usr/bin/env python3

#import boto3
import os
import subprocess
import glob
from sqlalchemy.orm import Query
from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import albumentations as A
import cv2
import re


Base = declarative_base()

DATA_FOLDER = '/home/andrei/Desktop/imachines/homework/fashion-dataset'
OUTPUT_FOLDER = '/home/andrei/Desktop/imachines/homework/out'
DB_URL = 'postgresql://postgres:postgres@localhost:5433/homework'


class StyleImage(Base):
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

def create(engine):
    Base.metadata.create_all(bind=engine)


def open_session(dbURL):
    engine = create_engine(dbURL)

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
    target_folder = os.path.join(OUTPUT_FOLDER, folder)
    try:
        os.makedirs(target_folder)
    except FileExistsError:
        # directory already exists
        pass        

    s = open_session(DB_URL)
    try:
        results = query.with_session(s)

        for item in results:
            print(f'Fetching item {item.file_id}')
            source_image_path = os.path.join(DATA_FOLDER, 'images', item.file_name)
            source_json_path = os.path.join(DATA_FOLDER, 'styles', f'{item.file_id}.json')
            # subprocess.call(["cp", source_image_path, target_image_path],shell=True)
            
            os.system(f'cp {source_image_path} {target_folder}') 
            os.system(f'cp {source_json_path} {target_folder}')
            # To Do s3 
            
    finally:
        s.close()


def augment_image(file, size=256):
    im = cv2.imread(file)
    aug = A.RandomResizedCrop(size, size, scale=(0.8, 0.8))
    augmented = aug(image=im)
    filename, file_extension = os.path.splitext(file) 
    cv2.imwrite(filename+'_au'+file_extension, augmented['image'])


def list_folder(folder):
    """ Utility function for notebook"""
    target_folder = os.path.join(OUTPUT_FOLDER, folder)
    images = [os.path.join(target_folder, f) for f in os.listdir(target_folder) if re.search(r'[0-9]+\.jpg$', f)]
    augmented_images = glob.glob(os.path.join(target_folder, '*_au.jpg'))
    styles = glob.glob(os.path.join(target_folder, '*.json'))
    images.sort()
    augmented_images.sort()
    styles.sort()
    return {'images':images, 'augmented_images':augmented_images, 'styles':styles}


def transform_folder(folder, size=256):
    original_images = list_folder(folder)
    for image_file in original_images['images']:
        augment_image(image_file, size)


if __name__ == "__main__":
    # process_query(Query(StyleImage).filter(StyleImage.year == 2011).limit(10), 'year2011')
    files = list_folder('year2011')
    print(files)
    transform_folder('year2011')
