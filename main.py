from src.analyzer import run_analyzer
import os
from dotenv import load_dotenv

load_dotenv()


path1 = os.getenv("PATH1")
path2 = os.getenv("PATH2")


run_analyzer(path1,path2)