#!/usr/bin/env python

from __future__ import print_function
import sys
import time
import pandas as pd
import string
import logging
import subprocess as sp


logger = logging.getLogger("STAR-SEQR")


def write_header(args, fh, file_type):
    '''Follow the spec here: https://samtools.github.io/hts-specs/VCFv4.2.pdf'''
    today = time.strftime('%m/%d/%Y')
    vpcmd = str(' '.join(sys.argv))
    vcf_head = '\t'.join(['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', args.prefix])
    bedpe_head = '\t'.join(['#CHROM_A', 'START_A', 'END_A', 'CHROM_B', 'START_B', 'END_B', 'ID', 'QUAL', 'STRAND_A', 'STRAND_B',
                            'TYPE', 'FILTER', 'NAME_A', 'REF_A', 'ALT_A', 'NAME_B', 'REF_B', 'ALT_B', 'INFO_A', 'INFO_B', 'FORMAT', args.prefix])
    header = ['##fileformat=VCFv4.2', '##fileDate=' + today,
              '##source=STAR-SV', '##reference=' + 'hg19',
              '##FILTER=<ID=PASS,Description="All filters passed">',
              '##FILTER=<ID=FAIL,Description="Site failed to reach confidence">',
              '##INFO=<ID=ANN,Number=.,Type=String,Description="Functional annotations: \'Symbol\'">',
              '##INFO=<ID=IMPRECISE,Number=0,Type=Flag,Description="Imprecise structural variation">',
              '##INFO=<ID=CIPOS,Number=2,Type=Integer,Description="Confidence interval around POS for imprecise variants">',
              '##INFO=<ID=CIEND,Number=2,Type=Integer,Description="Confidence interval around END for imprecise variants">',
              '##INFO=<ID=END,Number=1,Type=Integer,Description="End position of the variant described in this record">',
              '##INFO=<ID=HOMLEN,Number=-1,Type=Integer,Description="Length of base pair identical micro-homology at event breakpoints">',
              '##INFO=<ID=HOMSEQ,Number=.,Type=String,Description="Sequence of base pair identical micro-homology at event breakpoints">',
              '##INFO=<ID=MATEID,Number=.,Type=String,Description="ID of mate breakends">',
              '##INFO=<ID=EVENT,Number=1,Type=String,Description="ID of event associated to breakend">',
              '##INFO=<ID=SECONDARY,Number=0,Type=Flag,Description="Secondary breakend in a multi-line variants">',
              '##INFO=<ID=SEQLEN,Number=.,Type=String,Description="Length of assembled sequence of reads supporting breakpoint">',
              '##INFO=<ID=SVLEN,Number=-1,Type=Integer,Description="Difference in length between REF and ALT alleles">',
              '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
              '##ALT=<ID=DEL,Description="Deletion">',
              '##ALT=<ID=DUP,Description="Duplication">',
              '##ALT=<ID=DUP:TANDEM,Description="Tandem Duplication">',
              '##ALT=<ID=INS,Description="Insertion of novel sequence">',
              '##ALT=<ID=INV,Description="Inversion">',
              '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
              '##FORMAT=<ID=SP,Number=1,Type=String,Description="Number of paired discordant spanning reads">',
              '##FORMAT=<ID=JXL,Number=1,Type=String,Description="Number of reads coming from the left">',
              '##FORMAT=<ID=JXR,Number=1,Type=String,Description="Number of reads coming from the right">',
              '##FORMAT=<ID=SPU,Number=1,Type=String,Description="Number of unique paired discordant spanning reads">',
              '##FORMAT=<ID=JXLU,Number=1,Type=String,Description="Number of unique reads coming from the left">',
              '##FORMAT=<ID=JXRU,Number=1,Type=String,Description="Number of unique reads coming from the right">',
              '##FORMAT=<ID=GQ,Number=1,Type=String,Description="Genotype Quality">',
              '##FORMAT=<ID=AF,Number=1,Type=Float,Description="Allele Frequency">',
              '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Total Depth at position">',
              '##FORMAT=<ID=AD,Number=2,Type=Integer,Description="Allele depths of ref and alt alleles in that order">',
              '##FORMAT=<ID=FSAD,Number=2,Type=Integer,Description="Allele depths on forward strands of ref and alt alleles in that order">',
              '##FORMAT=<ID=SB,Number=1,Type=Float,Description="Strand bias">',
              '##FORMAT=<ID=BQ,Number=1,Type=Float,Description="Average Base Quality of ALT">',
              '##FORMAT=<ID=PV,Number=1,Type=Float,Description="Adjusted p-value">',
              '##variants_justified=left',
              '##STAR-SV_CMD=' + vpcmd]
    if file_type == "bedpe":
        header.append(bedpe_head)
    else:
        header.append(vcf_head)
    header_out = '\n'.join(header)
    print(header_out, file=fh)


def get_svtype_func(str1, str2, c1, c2):
    # Translocations are represented as BNDs
    if c1 != c2:
        svtype = "BND"
    else:
        # STAR notation is same as other tools after strand2 is flipped.
        if str(str1) == "+" and str(str2) == "+":
            svtype = "INV"
        elif str(str1) == "-" and str(str2) == "-":
            svtype = "INV"
        elif str(str1) == "+" and str(str2) == "-":
            svtype = "DEL"
        elif str(str1) == "-" and str(str2) == "+":
            svtype = "DUP"
    return svtype


def get_bnd_alt_func(c1, c2, s1, s2, str1, str2, which_bnd):
    if which_bnd == 'A':
        if str(str1) == "+" and str(str2) == "+":
            alt = "N" + "[" + str(c2) + ":" + str(s2) + "]"
        elif str(str1) == "-" and str(str2) == "-":
            alt = "[" + str(c2) + ":" + str(s2) + "[" + "N"
        elif str(str1) == "+" and str(str2) == "-":
            alt = "N" + "[" + str(c2) + ":" + str(s2) + "["
        elif str(str1) == "-" and str(str2) == "+":
            alt = "]" + str(c2) + ":" + str(s2) + "]" + "N"
    elif which_bnd == 'B':
        if str(str1) == "+" and str(str2) == "+":
            alt = "N" + "[" + str(c1) + ":" + str(s1) + "]"
        elif str(str1) == "-" and str(str2) == "-":
            alt = "[" + str(c1) + ":" + str(s1) + "[" + "N"
        elif str(str1) == "+" and str(str2) == "-":
            alt = "N" + "[" + str(c1) + ":" + str(s1) + "["
        elif str(str1) == "-" and str(str2) == "+":
            alt = "]" + str(c1) + ":" + str(s1) + "]" + "N"
    return alt

# "SEQLEN=" + df['velvet'].str.len().astype(int).astype(str)


def get_bedpestuff_func(df_in, svtype):
    if svtype == "BND":
        df = df_in[df_in['svtype'] == "BND"]
        if len(df.index) > 0:
            df['REF_A'] = "N"
            df['ALT_A'] = df.apply(lambda x: get_bnd_alt_func(x['c1'], x['c2'], x['s1'], x['s2'], x['st1'], x['st2'], "A"), axis=1)
            df['NAME_A'] = df['id'].astype(int).astype(str) + "_1"
            df['NAME_B'] = df['id'].astype(int).astype(str) + "_2"
            df['REF_B'] = "N"
            df['ALT_B'] = df.apply(lambda x: get_bnd_alt_func(x['c1'], x['c2'], x['s1'], x['s2'], x['st1'], x['st2'], "B"), axis=1)
            df['INFO_A'] = "SVTYPE=" + df['svtype'] + ';' + \
                "POS=" + df['s1'].astype(str) + ';' + \
                "END=" + df['s2'].astype(str) + ';' + \
                "ANN=" + df['ann'] + ';' + \
                "CIPOS=" + "0," + df['a1'] + ';' + \
                "HOMLEN=" + df['a1'] + ';' + \
                "MATEID=" + df['NAME_B'] + ';' + \
                "EVENT=" + df['id'].astype(str) + ';' + \
                "SEQLEN=" + df['velvet'].str.len().astype(str)
            df['INFO_B'] = "SVTYPE=" + df['svtype'] + ';' + \
                "POS=" + df['s1'].astype(str) + ';' + \
                "END=" + df['s2'].astype(str) + ';' + \
                "ANN=" + df['ann'] + ';' + \
                "CIPOS=" + "0," + df['a2'] + ';' + \
                "HOMLEN=" + df['a1'] + ';' + \
                "MATEID=" + df['NAME_A'] + ';' + \
                "EVENT=" + df['id'].astype(str) + ';' + \
                "SECONDARY" + ';' + \
                "SEQLEN=" + df['velvet'].str.len().astype(str)
    else:
        df = df_in[df_in['svtype'] != "BND"]
        if len(df.index) > 0:
            df['REF_A'] = "N"
            df['ALT_A'] = "<" + df['svtype'] + ">"
            df['NAME_A'] = df['id'].astype(int).astype(str)
            df['NAME_B'] = "."
            df['REF_B'] = "."
            df['ALT_B'] = "."
            df['INFO_A'] = "SVTYPE=" + df['svtype'] + ';' + \
                "POS=" + df['s1'].astype(str) + ';' + \
                "END=" + df['s2'].astype(str) + ';' + \
                "ANN=" + df['ann'] + ';' + \
                "CIPOS=" + "0," + df['a1'] + ';' + \
                "HOMLEN=" + df['a1'] + ';' + \
                "SVLEN=" + df['dist'].astype(str) + ';' + \
                "SEQLEN=" + df['velvet'].str.len().astype(str)
            df['INFO_B'] = "."
    return df


def write_bedpe(bkpt_path, out_bedpe, args):
    bedpe_fh = open(out_bedpe, 'w')
    write_header(args, bedpe_fh, "bedpe")
    try:
        df = pd.read_csv(bkpt_path, sep="\t", header=1)
    except:
        return
    df = df.reset_index()
    df['c1'], df['s1'], df['st1'], df['c2'], df['s2'], df['st2'], df['a1'], df['a2'] = zip(*df['name'].str.split(':').tolist())
    # STAR has second object flipped
    flipstr = string.maketrans("-+", "+-")
    df['st2'] = df['st2'].str.translate(flipstr)

    # Common stuff to BNDs and others
    df['e1'] = df['s1']
    df['e2'] = df['s2']
    df['s1'] = df['s1'].astype(int) - 1  # Convert start to 0-based coordinates
    df['s2'] = df['s2'].astype(int) - 1
    df['id'] = df['index'].astype(int) + 1
    df['qual'] = df['jxn_first_unique'] + df['jxn_second_unique']  # Eventually get a handle on a scoring metric besides number of reads
    df['svtype'] = df.apply(lambda x: get_svtype_func(x['st1'], x['st2'], x['c1'], x['c2']), axis=1)
    df['filter'] = "PASS"

    # Get unique to BNDs and others then merge
    pd.options.mode.chained_assignment = None  # default='warn'
    df_bnd = get_bedpestuff_func(df, "BND")
    df_nonbnd = get_bedpestuff_func(df, "nonBND")
    df2 = pd.concat([df_bnd, df_nonbnd], ignore_index=True).sort_values(['c1', 's1'], ascending=[True, True])   #

    df2['FORMAT'] = "GT:SP:JXL:JXR:SPU:JXLU:JXRU"
    df2[args.prefix] = "./." + ":" + df2['spans_disc_all'].astype(str) + ":" + df2['jxn_first_all'].astype(str) + ":" + df2['jxn_second_all'].astype(
        str) + ":" + df2['spans_disc_unique'].astype(str) + ":" + df2['jxn_first_unique'].astype(str) + ":" + df2['jxn_second_unique'].astype(str)
    outcols = ['c1', 's1', 'e1', 'c2', 's2', 'e2', 'id', 'qual', 'st1', 'st2', 'svtype', 'filter',
               'NAME_A', 'REF_A', 'ALT_A', 'NAME_B', 'REF_B', 'ALT_B', 'INFO_A', 'INFO_B', 'FORMAT', args.prefix]
    df2.to_csv(path_or_buf=bedpe_fh, header=False, sep='\t', columns=outcols, mode='a', index=False)
    logger.info("bedpe creation was succesful!")

def write_vcf(in_bed, out_vcf, cfg):
    sv_args = ['python', cfg['svtools_bedpetovcf'], '-b', in_bed, '-o', out_vcf]
    sv_args = map(str, sv_args)
    logger.info("*svtools Command: " + " ".join(sv_args))
    # run svtools
    try:
        p = sp.Popen(sv_args, stdout=sp.PIPE, stderr=sp.PIPE)
        stdout, stderr = p.communicate()
        if stdout:
            logger.info(stdout)
        if stderr:
            logger.error(stderr)
        if p.returncode != 0:
            logger.error("Error: svtools failed", exc_info=True)
            sys.exit(1)
    except (OSError) as o:
        logger.error("Exception: " + str(o))
        logger.error("sv Failed", exc_info=True)
        sys.exit(1)
    logger.info("VCF creation was succesful!")


def process(bkpt_path, args, cfg):
    bedpe_path = args.prefix + '_STAR-SEQR_breakpoints.bedpe'
    vcf_path = args.prefix + '_STAR-SEQR_breakpoints.vcf'
    write_bedpe(bkpt_path, bedpe_path, args)
    write_vcf(bedpe_path, vcf_path, cfg)
