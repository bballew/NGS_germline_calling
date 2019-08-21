#!/bin/sh

module load python3/3.6.3 sge
unset module
cmd="qsub -q xlong.q -V -j y -S /bin/sh -o ${PWD} /DCEG/CGF/Bioinformatics/Production/Bari/Germline_pipeline_v4_dev/germlineCallingV4/scripts/submit.sh ${PWD}/config.yaml"
echo "Command run: $cmd"
eval $cmd

