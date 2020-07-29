#!/usr/bin/env python3

from time import time
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


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


if __name__ == "__main__":
    t = time()

    #Create the database
    engine = create_engine(f'postgresql://postgres:postgres@localhost:5433/homework')
    Base.metadata.create_all(engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    try:
        # todo: set path as an argument
        images_file_name = "fashion-dataset/images.csv" 
        styles_file_name = "fashion-dataset/styles.csv" 

        # delete old data first as this is not an incremental update
        num_rows_deleted = s.query(StyleImage).delete()
        s.commit()
        print(f'Old rows deleted: {num_rows_deleted}')
        
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
                    print(f"Image file id {image_values[0]} doesn't correspond to style file id {style_values[0]} at line {line_num}")
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

            
            print(f'Total collected records {accepted_record_count}')

        s.commit() #Attempt to commit all the records
    except Exception as e:
        print(e)
        s.rollback() #Rollback the changes on error
    finally:
        s.close() #Close the connection

    time_elapsed = time() - t
    print(f'Time elapsed: {time_elapsed}')

    # checking amount of loaded recors
    inserted_rec_count = s.query(StyleImage).count()
    print(f'Inserted records: {inserted_rec_count}')

    # checking how many year records weren't properly converted
    missing_year_count = s.query(StyleImage).filter(StyleImage.year == -1).count()
    print(f'Records with missing year: {missing_year_count}')

    # checking how many id records weren't properly converted
    missing_id_count = s.query(StyleImage).filter(StyleImage.id == -1).count()
    print(f'Records with missing id: {missing_id_count}')
