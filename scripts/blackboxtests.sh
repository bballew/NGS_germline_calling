#!/bin/bash

# script a run of the snakemake workflow here, then do some diffs to compare output at various steps to "accepted" output

DATE=$(date +"%Y%m%d%H%M")
myInPath="/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/data/"
myOutPath="/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/out_${DATE}/"

if [ ! -d "$myOutPath" ]; then
    mkdir -p "$myOutPath" || die "mkdir ${myOutPath} failed"
else
    echo "${myOutPath} already exists!"
fi

# generate a test config:
echo "maxJobs: 100" > ${myOutPath}/TESTconfig.yaml
echo "inputDir: '${myInPath}'" >> ${myOutPath}/TESTconfig.yaml
echo "outputDir: '${myOutPath}'" >> ${myOutPath}/TESTconfig.yaml
echo "logDir: '${myOutPath}/logs/'" >> ${myOutPath}/TESTconfig.yaml
echo "tempDir: '/ttemp/bballew/${DATE}/'" >> ${myOutPath}/TESTconfig.yaml
echo "intervalFile: '/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/regions/seqcap_EZ_Exome_v3_v3utr_intersect_correct_NOchr4.intervals'" >> ${myOutPath}/TESTconfig.yaml
echo "bedFile: '/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/tests/regions/seqcap_EZ_Exome_v3_v3utr_intersect_correct_NOchr4.bed'" >> ${myOutPath}/TESTconfig.yaml
echo "clusterMode: 'qsub -q long.q -V -j y -o ${myOutPath}/logs/'" >> ${myOutPath}/TESTconfig.yaml
echo "snakePath: '/DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/scripts/'" >> ${myOutPath}/TESTconfig.yaml
echo "gatkPath: '/DCEG/Projects/Exome/SequencingData/GATK_binaries/gatk-4.0.11.0/'" >> ${myOutPath}/TESTconfig.yaml
echo "refGenome: '/DCEG/CGF/Bioinformatics/Production/Bari/refGenomes/hg19_canonical_correct_chr_order.fa'" >> ${myOutPath}/TESTconfig.yaml
echo "useShards: TRUE  # shards vs. chroms to parallelize" >> ${myOutPath}/TESTconfig.yaml
echo "numShards: 4" >> ${myOutPath}/TESTconfig.yaml
echo "modelPath: '/opt/wes/model.ckpt' # either /opt/wgs/model.ckpt or /opt/wes/model.ckpt for WGS or WES, respectively" >> ${myOutPath}/TESTconfig.yaml



module load python3/3.6.3 sge
unset module
cmd="qsub -q long.q -V -j y -S /bin/sh -o ${myOutPath} /DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/scripts/submit.sh ${myOutPath}/TESTconfig.yaml"
echo "Command run: $cmd"
eval $cmd
