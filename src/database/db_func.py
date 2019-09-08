from .db import *

# table: The Table object representing the table to insert into
# values: A list of the values for each column
# columns: A list of the columns to insert
def insert(table: Table, values: list, columns: list = None):
    for i in range(len(values)):
        if type(values[i]) is str:
            values[i] = "'{}'".format(values[i])
        else:
            values[i] = str(values[i])
    values_str = "(" + ", ".join(values) + ")"
    # Check if insert includes all columns
    if columns is None:
        sql = "INSERT INTO {} VALUES {};".format(table.name, values_str)
    else:
        columns_str = "(" + ", ".join(columns) + ")"
        sql = "INSERT INTO {} {} VALUES {};".format(table.name, columns_str, values_str)

    print(sql)
    return sql

# table: The Table object representing the table to update
# values: A list of the values for each column
# columns: A list of the columns to update
# entry_id: The primary key of the entry to update
def update(table: Table, columns: list, values: list, entry_id: int):
    # map values to table.columns
    set_tuple = list(zip(columns, values))
    set_list = []
    for t in set_tuple:
        if type(t[1]) is str:
            set_list.append(t[0] + " = '" + t[1] + "'")
        else:
            set_list.append(t[0] + " = " + str(t[1]))
    set_str = ", ".join(set_list)

    sql = "UPDATE {} SET {} WHERE {};".format(table.name, set_str, where(table[0], entry_id))
    print(sql)
    return sql

# table: The Table object representing the table to select from
# columns: A list of the columns to fetch
# conditions: A list of two or three-tuples representing Where clauses
# order: A two tuple, 0th for parameter, 1st for order (0 for ASC, 1 for DESC)
# limit: The max number of entries to retrieve
def select(table: Table, columns: list = None, conditions: list = None, order: tuple = None, limit: int = 0):
    # Table and columns
    sql = "SELECT {} FROM {}"
    if columns is None:
        sql = sql.format("*", table.name)
    else:
        sql = sql.format(", ".join(columns), table.name)

    # Where clause, passed as list of tuples
    if conditions is not None:
        sql += where_clause(conditions)

    # Order by
    if order is not None:
        if order[1] == 0:
            sql += " ORDER BY {} ASC".format(order[0])
        elif order[1] == 1:
            sql += " ORDER BY {} DESC".format(order[0])

    # Limit
    if limit > 0:
        sql += " LIMIT {}".format(limit)

    print(sql)
    return sql + ";"

# table: The Table object representing the table to count from
# count_arg: The argument for the COUNT() function
# conditions: A list of two or three-tuples representing Where clauses
# group: The column to group by
def count(table: Table, count_arg: str = '*',  conditions: list = None, group: str = None):
    sql = "SELECT COUNT({}) as counts FROM {}".format(count_arg, table.name)

    if conditions is not None:
        sql += where_clause(conditions)

    if group is not None:
        sql += " GROUP BY {}".format(group)

    return sql + ";"

def where(field: str, value, op: str = "="):
    if type(value) is str:
        return "{} {} '{}'".format(field, op, value)
    else:
        return "{} {} {}".format(field, op, value)

def where_clause(conditions: list):
    print(conditions)
    condition_list = []
    for c in conditions:
        if len(c) == 3:
            condition_list.append(where(c[0], c[1], c[2]))
        else:
            condition_list.append(where(c[0], c[1]))

    condition_str = " WHERE " + " AND ".join(condition_list)
    return condition_str

