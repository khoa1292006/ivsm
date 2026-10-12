import pandas as pd

df = pd.read_csv("data/Iris.csv")

print(df.head())
print("\nKích thước dữ liệu:", df.shape)
print("\nTên các cột:")
print(df.columns)
