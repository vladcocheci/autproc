# autproc
code for downloading and processing building approvals in Cluj-Napoca

to use:
docker run -v <HOST_FOLDER>:/usr/src/autproc autproc 'yyyy' 'no_of_first_approval' 'no_of_last_approval'

example:
docker run -v ~/Git/autproc:/usr/src/autproc autproc '2018' '1' '10'
