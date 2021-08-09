'''
Descripttion: 
version: 
Author: sueRimn
Date: 2021-07-30 16:18:22
LastEditors: sueRimn
LastEditTime: 2021-07-30 16:19:18
'''
import query_file_attrs

if __name__ == "__main__":
    check = query_file_attrs.ParseAndCheckArg()
    file_attrs_lists = check.parse_and_check()

    for file_attrs in file_attrs_lists:
        test = query_file_attrs.QueryFileAttrs(file_attrs)
        result = test.query_file_attrs()
        for res in result:
            print(res)