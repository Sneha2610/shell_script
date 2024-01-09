# Python script to fetch lines starting and ending with specific strings
# from file1.txt and concatenate them with file2.txt

start_string = "Start"
end_string = "End"

# Read lines from file1.txt that start and end with specific strings
with open('file1.txt', 'r') as file1:
    lines_to_concatenate = [line.strip() for line in file1 if line.startswith(start_string) and line.endswith(end_string)]

# Read the contents of file2.txt
with open('file2.txt', 'r') as file2:
    file2_contents = file2.read()

# Concatenate lines from file1.txt with contents of file2.txt
result = '\n'.join(lines_to_concatenate) + '\n' + file2_contents

# Write the result back to file2.txt
with open('file2.txt', 'w') as file2:
    file2.write(result)

print("Concatenation complete.")
