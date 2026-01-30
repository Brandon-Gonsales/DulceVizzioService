import asyncio
import json
from bson import ObjectId
from datetime import datetime
from pydantic import HttpUrl
from app.database import connect_to_mongo
from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, HttpUrl):
            return str(obj)
        if hasattr(obj, 'model_dump'):
             return obj.model_dump(mode='json')
        return super().default(obj)

async def extract_examples():
    try:
        await connect_to_mongo()
        
        user = await User.find_one({})
        if user:
            with open('example_user.json', 'w', encoding='utf-8') as f:
                json.dump(user.model_dump(mode='json'), f, cls=MongoEncoder, indent=2)

        course = await Course.find_one({})
        if course:
            with open('example_course.json', 'w', encoding='utf-8') as f:
                json.dump(course.model_dump(mode='json'), f, cls=MongoEncoder, indent=2)

        lesson = await Lesson.find_one({})
        if lesson:
            with open('example_lesson.json', 'w', encoding='utf-8') as f:
                json.dump(lesson.model_dump(mode='json'), f, cls=MongoEncoder, indent=2)
            
        enrollment = await Enrollment.find_one({})
        if enrollment:
            with open('example_enrollment.json', 'w', encoding='utf-8') as f:
                 json.dump(enrollment.model_dump(mode='json'), f, cls=MongoEncoder, indent=2)
                 
        print("Archivos JSON generados exitosamente.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(extract_examples())
