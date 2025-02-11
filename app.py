from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import spacy
import random
import os

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://xforce:Admin1234@smarthackathon.azjsv.mongodb.net/userDB")

# Load SpaCy model (optimized for English processing)
nlp = spacy.load("en_core_web_sm")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["userDB"]

# Predefined list of skills
SKILL_KEYWORDS = {"Python", "Machine Learning", "Data Analysis", "JavaScript", "React", "MongoDB", "Java", "C++", "HTML", "SQL", "AI", "Django", "Flask"}

# Initialize FastAPI
app = FastAPI()

# Define request model
class Query(BaseModel):
    user_input: str

# Extract skills from input text
def extract_skills(input_text: str):
    extracted_skills = {skill for skill in SKILL_KEYWORDS if skill.lower() in input_text.lower()}
    return list(extracted_skills)

# Search users by skills
def search_users_by_skills(input_skills):
    users = db.users.find({"skills": {"$in": input_skills}}, {"_id": 0, "username": 1, "skills": 1})
    return [{"Username": user["username"], "Matched Skills": list(set(input_skills) & set(user["skills"]))} for user in users]

# Search teams by skills
def search_teams_by_skills(input_skills):
    teams = db.teams.find({"skillsRequired": {"$in": input_skills}}, {"_id": 0, "teamName": 1, "skillsRequired": 1, "slotsAvailable": 1})
    return [{"Team Name": team["teamName"], "Matched Skills": list(set(input_skills) & set(team["skillsRequired"])), "Slots Available": team["slotsAvailable"]} for team in teams]

# Show all users
def show_all_users():
    return list(db.users.distinct("username"))

# Show all teams
def show_all_teams():
    return list(db.teams.find({}, {"_id": 0, "teamName": 1, "skillsRequired": 1, "slotsAvailable": 1}))

# Generate chatbot responses
def chatbot_response(user_input):
    responses =  [
    "At this MVP stage, we can only suggest teams and users based on your skills. Let me know what skills you have!",
    "I couldn't find any relevant skills in your input. Please try again with skills like Python, AI, Java, etc.",
    "Currently, we only match users and teams based on skills. More features are coming soon!",
    "Looking for a team or users? Just tell me your skills, and I’ll find the best matches for you!",
    "Right now, we focus on skill-based matching. In future updates, we’ll add more smart features!",
    "I'm still learning! Right now, I can only help you find teams or users based on skills."
]
    return random.choice(responses)

# API endpoints
@app.post("/search")
async def search(query: Query):
    user_input = query.user_input.lower()
    
    if "show all users" in user_input:
        return {"status": "success", "data": show_all_users(), "message": "All users retrieved successfully."}
    
    if "show all teams" in user_input:
        return {"status": "success", "data": show_all_teams(), "message": "All teams retrieved successfully."}
    
    extracted_skills = extract_skills(user_input)
    if not extracted_skills:
        return {"status": "error", "message": chatbot_response(user_input)}
    
    if "user" in user_input:
        return {"status": "success", "data": search_users_by_skills(extracted_skills), "message": "Users matching skills found."}
    
    if "team" in user_input:
        return {"status": "success", "data": search_teams_by_skills(extracted_skills), "message": "Teams matching skills found."}
    
    return {"status": "error", "message": chatbot_response(user_input)}




