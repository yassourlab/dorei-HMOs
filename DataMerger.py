#!/usr/bin/env python3

import pandas as pd
import csv
import argparse

MEDIA = "media"
SPCS = "sample"
WELL = "well"
TIME = "Time"
BIO_REP = "biological replicate"
TEC_REP = "technical replicate"


DESCRIPTION = "Growth curve merger for Sivan K"
INPUT_HELP_IN_TABLE = "table with species names and mapping keys to sample"
INPUT_HELP_IN_DATA = "experiment data to analayse"
INPUT_HELP_RANGE = "range of data table <format: 37:120>"


def parse_input():
    """ parser of input """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument("table_in",
                        metavar="table_in",
                        help=INPUT_HELP_IN_TABLE)
    parser.add_argument("data_in",
                        metavar="data_in",
                        help=INPUT_HELP_IN_DATA)
    parser.add_argument("-r", "--range",
                        nargs='?',
                        type=str,
                        help=INPUT_HELP_RANGE)

    # TODO: add this arg, if needed
    # parser.add_argument("out_file_path",
    #                     metavar="path_to_out",
    #                     default="merged_grow_curve.txt",
    #                     help=INPUT_HELP_OUTPATH)

    all_args = parser.parse_args()
    return all_args


def parse_in_files(all_args, start_row, end_row):
    """ Reads the input files (csv or xlsx) and returns its dfs """
    try:
        df = pd.read_excel(all_args.table_in)
        raw_df = pd.read_excel(all_args.data_in,
                               skiprows=start_row,
                               nrows=end_row-start_row)
        pd.options.mode.chained_assignment = None
    except Exception:   # TODO: change to exact exception type
        df = pd.read_csv(all_args.table_in)
        raw_df = pd.read_csv(all_args.data_in,
                             skiprows=start_row,
                             nrows=end_row-start_row)
        pd.options.mode.chained_assignment = None
    return df, raw_df


def write_to_file(df, exp, out_file):
    df.insert(0, MEDIA, exp[1])
    df.insert(0, SPCS, exp[0])
    df.to_csv(out_file, index=False, mode='a', header=False)
    # out_file.write("\n\n")


def write_header(out_file):
    header = [
        SPCS, MEDIA, TIME,
        '1.1',
        '1.2',
        '1.3',
        '2.1',
        '2.2',
        '2.3']

    for h in header:
        out_file.write(str(h)+', ')
    out_file.write('\n')


def find_main_table(table_file_path):
    search_word = ('Time', 'Results')
    start_row = 0
    end_row = 0
    reader = csv.reader(open(table_file_path, 'r'))
    for i, data in enumerate(reader, start=0):
        if search_word[0] in data and data[3]:
            start_row = i
        elif search_word[1] in data:
            end_row = i
            break

    return start_row, end_row



def grab_data(df, raw_df, out_file):
    """ Runs a cycle of grabbing data from both files and writing it to out"""
    NA_THRSHLD = 5
    raw_df = raw_df.dropna(thresh=NA_THRSHLD)
    curr_group = [TIME]

    for i in range(df.shape[0]):   # all rows of table
        well = df.iloc[i][WELL]
        species = df.iloc[i][SPCS]
        media = df.iloc[i][MEDIA]
        bio_rep = df.iloc[i][BIO_REP]
        tec_rep = df.iloc[i][TEC_REP]

        if bio_rep == 1 and tec_rep == 1 and i > 0:
            write_to_file(raw_df[list(curr_group)], curr_exp, out_file)
            curr_group = [TIME]

        curr_group.append(well)
        curr_exp = (species, media)

    write_to_file(raw_df[list(curr_group)], curr_exp, out_file)
    curr_group = [TIME]


def main():
    # input processing
    all_args = parse_input()
    if all_args.range:
        start_row, end_row = all_args.range.split(':')
        start_row, end_row = int(start_row), int(end_row)
    else:
        start_row, end_row = find_main_table(all_args.data_in)

    # out file creations
    out_file = open('out.csv', 'w')
    write_header(out_file)

    # data frames
    df, raw_df = parse_in_files(all_args, start_row, end_row)
    grab_data(df, raw_df, out_file)

    out_file.close()

if __name__ == "__main__":
    main()
