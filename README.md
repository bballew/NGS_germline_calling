# Germline SNV calling pipeline v4
## Joint variant calling with GATK4 HaplotypeCaller and Google DeepVariant, coordinated via Snakemake.


## Introduction

This pipeline can be used to call germline SNVs and small indels for WGS/WES short read germline sequencing data.  

__Input:__
- Aligned and indexed BAM files
- Edited `config.yaml` file

__Output:__
- Depends on run mode selected in the config, but can include:
  - Multi-sample VCF called with DeepVariant
  - Multi-sample VCF called with HaplotypeCaller
  - Multi-sample VCF containing the union of the DeepVariant and HaplotypeCaller calls

## How to run:

1. Copy `config.yaml` to your working directory and edit as necessary
2. Copy `run_pipeline.sh` to your working directory and edit as necessary
3. Run via `bash run_pipeline.sh`
4. Monitor progress by looking at `log_<datetime>.out` in the log directory (set in the config file).

## Configuring the pipeline

- Most options are self-explanatory
- The pipeline will run over all *.bam files in the `inputDir`
- `clusterMode` can be the cluster submission string (e.g. `qsub ...`) or a few keywords:
  - `local` to run the pipeline on a single machine
  - `unlock` to unlock the working directory (may be needed if snakemake exited unexpectedly - see snakemake docs for details)
- `useShards` is a boolean to allow parallelization of DeepVariant over shards (e.g. if numShards=10, then each "shard" will contain 10% of the data) or over chromosomes
  - For targeted analyses that only cover a subset of chromosomes, use `useShards: TRUE`.  Using by-chromosome parallelization will result in empty datasets which will cause errors during calling with DeepVariant.
- `modelPath` has two options provided by DeepVariant, /opt/wgs/model.ckpt or /opt/wes/model.ckpt for WGS or WES, respectively


__Run modes:__
- HaplotypeCaller only
- DeepVariant only
- Both callers, no harmonized output
- Both callers plus harmonized output
- Harmonized output only - CURRENTLY UNTESTED - only applicable to caller output/directory structure as would be created by the calling modules of this pipeline
- Set the run mode for a given pipeline execution in the config as follows:
  - Example: DeepVariant only

      runMode:
        haplotypeCaller: FALSE
        deepVariant: TRUE
        harmonize: FALSE

  - Example: Both callers plus harmonized output

      runMode:
        haplotypeCaller: TRUE
        deepVariant: TRUE
        harmonize: TRUE


## How to perform black box testing to identify regressions and confirm expected output

- Open `scripts/blackboxtests.sh` and edit `myInPath` and `myOutPath` if necessary
- Run via `bash scripts/blackboxtests.sh`
  - This will create config files and execute five independent pipeline runs, one in each of the following run modes:
    - HaplotypeCaller only, output to `tests/out_<datestamp>_HC`
    - DeepVariant only, output to `tests/out_<datestamp>_DV`
    - Both callers, no harmonized output, output to `tests/out_<datestamp>_DV_HC`
    - Both callers plus harmonized output, output to `tests/out_<datestamp>_DV_HC_Har`
    - DeepVariant only, using by-chrom parallelization, output to `tests/out_<datestamp>_DV_by_chrom`
- Upon completion, run `bash scripts/blackboxdiffs.sh <datestamp>`, where `<datestamp>` is the date appended to the test run's `tests/out_<datestamp>_*` directory
- Look for PASS/ERROR status of each test (printed to stdout and saved to a file `tests/out_<datestamp>_*/diff_tests.txt`
  - NOTE: The DV_by_chrom test will fail, because DeepVariant errors out when there is no data for a given chromosome.  Consider using an alternative input dataset for this test.







------------------------------------------------


## To do:
__MOVE TO ISSUES.__
- Compare GATK and bcftools for concatenation of HaplotypeCaller VCFs and choose one
- Possibly add variant- and allele-level annotations
- Implement parallelization by region for merging with GLnexus
- Optimize environment for GLnexus performance (see https://github.com/dnanexus-rnd/GLnexus/wiki/Performance)
- Test DV parallel-by-chromosome option
- Compare DV performance of 23 shards vs. 23 chromosomes
- Test on 72 CTRL WES samples
- Test on 2 syndip WGS samples
- Add HTML report via Snakemake
- Consider how best to integrate with upstream production pipeline, e.g. merging config options and/or sourcing them from an earlier config file
- Think about how to handle differing metrics from GATK vs. DeepVariant



## Pipeline/HPC Failure Scenarios Test 
  1. Job failure by itself. (java error, memory issue, core dump, etc.)
      + without output.
      + with partial output.
  2. Job failed due to cluster issue. (job killed by the cluster)
      + without output.
      + with partial output.
  3. Job entered in to eqw/dr status (not easy to simulate, let’s be creative here)
  4. Job stuck in the “r” status (Snakemake will simply wait under this situation, which is expected and not very harmful, other than wasting computational time until the user realizes it)   
  5. Any other error scenario…?
      + How to work with Empty or Incomplete Directories
      + Resumability of an analyis (for example - gvcf generation job) from the beginning or from the point it got interrupted??
      + Voluntary Termination vs Interupted Jobs