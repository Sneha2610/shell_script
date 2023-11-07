# Define the names of the input HTML files and the output file
input_file1 = "file1.html"
input_file2 = "file2.html"
output_file = "combined.html"

# Read the contents of the first HTML file
with open(input_file1, "r") as file1:
    content1 = file1.read()

# Read the contents of the second HTML file
with open(input_file2, "r") as file2:
    content2 = file2.read()

# Combine the contents of both files
combined_content = content1 + content2

# Write the combined content to the output HTML file
with open(output_file, "w") as output:
    output.write(combined_content)

print(f"Combined HTML written to {output_file}")
