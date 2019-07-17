# wilee_jack_kelly
WILEE project for Cyber Hunting


### Code Review from MyPy, Black, and Flake8
To setup a pre-commit hook that runs MyPy, Black, and Flake8 on
python files staged for commit, navigate to the scripts directory
and run: 

`bash install-hooks.sh`

As a note, **this will delete any other pre-commit hook** that 
currently exists. If you would like to add more hooks or modify
the existing ones, simply modify the pre-commit.sh file in the
scripts directory.


To run the code check on an individual python file without 
committing, from the scripts directory run:

`bash ind_file_code_check.sh {path to python file to check}`

To run the code check on all the files staged for commit without
attempting to commit, from the scripts directory run:

`bash pre-commit.sh`