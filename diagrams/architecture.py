# diagram.py
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.onprem.client import Users
from diagrams.gcp.database import SQL
from diagrams.onprem.workflow import Airflow
from diagrams.programming.framework import Fastapi
from diagrams.custom import Custom
from diagrams.digitalocean.storage import Volume



with Diagram("Architecture", show=False):
    dropbox = Custom("Data Source (fashion.zip)", "./resources/dropbox.png")
    dag = Airflow("DAG")
    shared_volume = Volume("Data Store")
    streamlit = Custom("UI", "./resources/streamlit.jpg")
    azure = Custom("Azure CV", "./resources/azure.jpg")
    user  = Users("End User") 
    
    user >> streamlit
    streamlit >> user
    shared_volume >> streamlit
    dag >> shared_volume
    shared_volume >> dag
    dropbox >> dag
    streamlit >> Edge() << azure
    
