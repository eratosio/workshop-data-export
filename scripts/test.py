import pandas as pd
technologies = {
    'Courses':["Spark","PySpark","Python","pandas",None],
    'Fee' :[20000,25000,22000,None,30000],
    'Duration':['30days','40days','35days','None','50days'],
    'Discount':[1000,2300,1200,2000,None]
              }
index_labels=['r1','r2','r3','r4','r5']
df = pd.DataFrame(technologies,index=index_labels)
print(df)

# # Using DataFrame.mean() method to get column average
# df2 = df["Fee"].mean()
# print(df2)

# # Using DataFrame.mean() to get entire column mean
# df2 = df.mean()
# print(df2)

# Using multiple columns mean using DataFrame.mean()
df2 = df[["Fee","Discount"]].mean()
print(df2)

# # Average of each column using DataFrame.mean()
# df2 = df.mean(axis=0)
# print(df2)

# # Find the mean ignoring NaN values using DataFrame.mean()
# df2 = df.mean(axis = 0, skipna = False)
# print(df2)

# # Using DataFrame.describe() method
# df2 = df.describe()
# print(df2)