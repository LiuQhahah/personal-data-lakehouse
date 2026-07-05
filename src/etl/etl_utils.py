"""
ETL 工具：数据采集 -> Parquet -> MinIO
"""
import json
import os
import io
from datetime import datetime
from minio import Minio
import pyarrow as pa
import pyarrow.parquet as pq

# MinIO 配置
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "data"


class MinIOClient:
    def __init__(self):
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        if not self.client.bucket_exists(MINIO_BUCKET):
            self.client.make_bucket(MINIO_BUCKET)
            print(f"Created bucket: {MINIO_BUCKET}")
    
    def upload_json(self, data: list, source: str, date: str = None):
        """上传原始 JSON 数据"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        object_name = f"raw/{source}/{date}.json"
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.client.put_object(
            MINIO_BUCKET,
            object_name,
            io.BytesIO(json_str.encode()),
            len(json_str)
        )
        print(f"✅ Uploaded: {object_name}")
        return object_name
    
    def upload_parquet(self, df, source: str, layer: str = "bronze"):
        """上传 Parquet 数据"""
        table = pa.Table.from_pandas(df)
        buffer = io.BytesIO()
        pq.write_table(table, buffer)
        buffer.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        object_name = f"{layer}/{source}/data_{timestamp}.parquet"
        
        self.client.put_object(
            MINIO_BUCKET,
            object_name,
            buffer,
            length=buffer.getbuffer().nbytes
        )
        print(f"✅ Uploaded: {object_name}")
        return object_name
    
    def read_parquet(self, object_name: str):
        """从 MinIO 读取 Parquet"""
        response = self.client.get_object(MINIO_BUCKET, object_name)
        return pq.read_table(io.BytesIO(response.read()))
    
    def list_objects(self, prefix: str = ""):
        """列出对象"""
        return list(self.client.list_objects(MINIO_BUCKET, prefix=prefix))


def load_json_data(filepath: str) -> list:
    """加载本地 JSON 文件"""
    with open(filepath) as f:
        data = json.load(f)
    # 处理不同的 JSON 格式
    if isinstance(data, dict):
        if 'data' in data:
            return data['data']
    return data
