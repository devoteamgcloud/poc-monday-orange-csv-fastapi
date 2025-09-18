### Delta

1. Import delta CSV, separating projects and subtasks
2. Query Monday for projects in CSV by CSV Key
    
    ! use cursor for pagination
    ! assign result to a dictionnary
3. Compare CSV projects with Monday query result and format data to insert new projects and update existing ones
4. Apply the mutations
5. Repeat steps 2 3 4 for subtasks




TODO:
test fetch times for full boards
take name modification into account
deploy to monday code

QUESTIONS
Can projects/subtasks be deleted from or added to Jira?
What information will change?
