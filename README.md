# Germline SNV calling pipeline v4
## Joint variant calling with GATK4 HaplotypeCaller and Google DeepVariant, coordinated via Snakemake.


## Introduction
This Pipeline will serve as a CGR WGS/WES Germline Variant Calling pipeline for internal or external projects.  The pipeline takes calibrated and indexed BAMs as input and generates two compressed and indexed multi-sample VCFs file as final output - one with DeepVariant calls and one with GATK4 HaplotypeCaller calls.  These VCFs can then be fed into the ensemble bcbio pipeline.


## How to run:

1. Copy `config.yaml` to your working directory and edit as necessary
2. Copy `run_pipeline.sh` to your working directory and edit as necessary
3. Run via `bash run_pipeline.sh`

## Configuring the pipeline

- Most options are self-explanatory
- The pipeline will run over all *.bam files in the `inputDir`
- `clusterMode` can be the cluster submission string (e.g. `qsub ...`) or a few keywords:
  - `local` to run the pipeline on a single machine
  - `unlock` to unlock the working directory (may be needed if snakemake exited unexpectedly - see snakemake docs for details)
- `useShards` is a boolean to allow parallelization of DeepVariant over shards (e.g. if numShards=10, then each "shard" will contain 10% of the data) or over chromosomes
- `modelPath` has two options provided by DeepVariant, /opt/wgs/model.ckpt or /opt/wes/model.ckpt for WGS or WES, respectively


------------------------------------------------


## To do:

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
  
  
