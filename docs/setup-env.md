Setting Up the Environment

To prepare the project for development, follow these steps:
	1.	Ensure poetry is installed:
If you don’t have Poetry installed, you can install it using the following command:

curl -sSL https://install.python-poetry.org | python3 -

Or check the official Poetry installation guide.

	2.	Install dependencies:
Run the following command to install all dependencies from the pyproject.toml file:

poetry install


	3.	Set up the .env file:
Execute the following command to generate a .env file from the example.env template:

poetry run setup-env

This command will:
	•	Create a .env file in the project root if it doesn’t already exist.
	•	Copy all default values from the example.env file.

	4.	Verify the .env file:
Open the .env file in the project root and ensure all necessary environment variables are correctly set.
	5.	Run the project:
Start the project using your preferred method, e.g., docker-compose, poetry run, or another command depending on your setup.

Notes:
	•	If you encounter any issues, ensure that example.env exists in the project root and contains the default values.
	•	The .env file is ignored by version control (.gitignore) to protect sensitive information.