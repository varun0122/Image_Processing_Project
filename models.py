from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProcessingRequest(Base):
    __tablename__ = 'processing_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(36), unique=True, nullable=False)
    status = Column(String(20), nullable=False)
    csv_file_path = Column(Text, nullable=False)

    def __repr__(self):
        return f"<ProcessingRequest(request_id={self.request_id}, status={self.status})>"

class ProductImage(Base):
    __tablename__ = 'product_image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String(50), nullable=False)
    product_name = Column(String(100), nullable=False)
    original_url = Column(Text, nullable=False)
    processed_image_path = Column(Text, nullable=False)
    output_url = Column(Text, nullable=False)
    request_id = Column(String(36), nullable=False)  # Foreign key to ProcessingRequest

    def __repr__(self):
        return (f"<ProductImage(serial_number={self.serial_number}, product_name={self.product_name}, "
                f"original_url={self.original_url}, processed_image_path={self.processed_image_path}, "
                f"output_url={self.output_url}, request_id={self.request_id})>")

# Optionally, include code to create tables in the database
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # SQLAlchemy setup for MySQL
    engine = create_engine('mysql+mysqlconnector://username:password@localhost:3306/mydatabase')
    # Note that username, password, mydatabase(database name) should be replaced according to one's credentials
    Base.metadata.create_all(engine)
    print("Tables created successfully!")