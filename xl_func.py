import xlwings as xw


@xw.func
def Test(a, b):
    return a + b


if __name__ == "__main__":
    xw.server()
