### Exercise Search API Documentation

#### Base URL
```
http://127.0.0.1:5000/
```

#### Endpoint: Search Exercises by Main Muscle

**URL**: `/search`

**Method**: `GET`

**Query Parameters**:
- `main_muscle` (required): The main muscle group to search for exercises. This parameter supports partial matches.

**Response**: JSON array of exercises matching the search criteria.

**Status Codes**:
- `200 OK`: Request succeeded, and the response body contains the matching exercises.
- `400 Bad Request`: The `main_muscle` parameter is missing.

**Example Request**:
```
GET /search?main_muscle=Deltoid
```

**Example Response**:
```json
[
    {
        "Exercise_Name": "Overhead Press",
        "Equipment": "Barbell",
        "Variation": "No",
        "Utility": "Basic",
        "Mechanics": "Compound",
        "Force": "Push",
        "Preparation": "Stand with feet shoulder-width apart.",
        "Execution": "Press the barbell overhead until arms are fully extended.",
        "Target_Muscles": "Deltoid",
        "Synergist_Muscles": "Triceps Brachii",
        "Stabilizer_Muscles": "Core",
        "Antagonist_Muscles": "Latissimus Dorsi",
        "Dynamic_Stabilizer_Muscles": "None",
        "Main_muscle": "Deltoid",
        "Difficulty": 3,
        "Secondary_Muscles": "Triceps Brachii",
        "parent_id": null
    },
    ...
]
```

### Main Muscle Groups

Below is a list of all possible main muscle groups that can be searched:

- Adductor Brevis
- Adductor Longus
- Adductor Magnus
- Anterior
- Brachialis
- Brachioradialis
- Cervicis & Capitis Fibers
- Clavicular
- Coracobrachialis
- Deltoid
- Erector Spinae (see notes)
- Erector Spinae
- Flexor Carpi Ulnaris
- Gastrocnemius (Second Leg)
- Gastrocnemius (following leg)
- Gastrocnemius (second leg)
- Gastrocnemius
- Gluteus Maximus
- Gluteus Medius
- Gluteus Minimus
- Gluteus minimus
- Gracilis
- Hamstrings (top half)
- Infraspinatus
- Lateral
- Lower Fibers
- Lower
- Middle Trapezius
- Middle
- Obliques
- Pectineus
- Pectoralis Major
- Pectoralis Minor
- Piriformis
- Popliteus
- Posterior
- Psoas major
- Rectus Femoris
- Rhomboids
- Sartorius
- Soleus
- Sternal
- Sternocleidomastoid
- Supraspinatus
- Teres Major
- Teres Minor
- Trapezius
- Triceps Brachii
- Triceps
- Upper
- "Adductor Magnus" (with leading/trailing quotes)
- "Anterior" (with leading/trailing quotes)
- "Brachialis" (with leading/trailing quotes)
- "Brachioradialis" (with leading/trailing quotes)
- "Cervicis & Capitis Fibers" (with leading/trailing quotes)
- "Clavicular" (with leading/trailing quotes)
- "Coracobrachialis" (with leading/trailing quotes)
- "Deltoid" (with leading/trailing quotes)
- "Erector Spinae" (with leading/trailing quotes)
- "Flexor Carpi Ulnaris" (with leading/trailing quotes)
- "Gastrocnemius (Second Leg)" (with leading/trailing quotes)
- "Gastrocnemius (following leg)" (with leading/trailing quotes)
- "Gastrocnemius (second leg)" (with leading/trailing quotes)
- "Gastrocnemius" (with leading/trailing quotes)
- "Gluteus Maximus" (with leading/trailing quotes)
- "Gluteus Medius" (with leading/trailing quotes)
- "Gluteus Minimus" (with leading/trailing quotes)
- "Gluteus minimus" (with leading/trailing quotes)
- "Gracilis" (with leading/trailing quotes)
- "Hamstrings (top half)" (with leading/trailing quotes)
- "Infraspinatus" (with leading/trailing quotes)
- "Lateral" (with leading/trailing quotes)
- "Lower Fibers" (with leading/trailing quotes)
- "Lower" (with leading/trailing quotes)
- "Middle Trapezius" (with leading/trailing quotes)
- "Middle" (with leading/trailing quotes)
- "Obliques" (with leading/trailing quotes)
- "Pectineus" (with leading/trailing quotes)
- "Pectoralis Major" (with leading/trailing quotes)
- "Pectoralis Minor" (with leading/trailing quotes)
- "Piriformis" (with leading/trailing quotes)
- "Popliteus" (with leading/trailing quotes)
- "Posterior" (with leading/trailing quotes)
- "Psoas major" (with leading/trailing quotes)
- "Rectus Femoris" (with leading/trailing quotes)
- "Rhomboids" (with leading/trailing quotes)
- "Sartorius" (with leading/trailing quotes)
- "Soleus" (with leading/trailing quotes)
- "Sternal" (with leading/trailing quotes)
- "Sternocleidomastoid" (with leading/trailing quotes)
- "Supraspinatus" (with leading/trailing quotes)
- "Teres Major" (with leading/trailing quotes)
- "Teres Minor" (with leading/trailing quotes)
- "Trapezius" (with leading/trailing quotes)
- "Triceps Brachii" (with leading/trailing quotes)
- "Triceps" (with leading/trailing quotes)
- "Upper" (with leading/trailing quotes)
- "No significant stabilizers" (with leading/trailing quotes)
- "Biceps Brachii" (with leading/trailing quotes)
- "Brachialis" (with leading/trailing quotes)
- "Deltoid" (with leading/trailing quotes)
- "Erector Spinae" (with leading/trailing quotes)
- "Gastrocnemius" (with leading/trailing quotes)
- "Gluteus Medius" (with leading/trailing quotes)
- "Hamstrings" (with leading/trailing quotes)
- "Infraspinatus" (with leading/trailing quotes)
- "Lateral Deltoid" (with leading/trailing quotes)
- "Latissimus Dorsi" (with leading/trailing quotes)
- "Obliques" (with leading/trailing quotes)
- "Pectoralis Major Sternal" (with leading/trailing quotes)
- "Pectoralis Major" (with leading/trailing quotes)
- "Posterior Deltoid" (with leading/trailing quotes)
- "Tensor Fasciae Latae" (with leading/trailing quotes)
- "Trapezius" (with leading/trailing quotes)
- "Triceps Brachii" (with leading/trailing quotes)
- "Wrist Flexors" (with leading/trailing quotes)
- "keeping back straight and knees pointed same direction as feet. Squat down until thighs are just past parallel to floor. Return and repeat." (with leading/trailing quotes)
- "pulling heels toward rear end while keeping hips and low back straight. Raise up until lower legs are vertical or fully flexed. Lower body to original position by straightening knees" (with leading/trailing quotes)
- "push body up until arms are straight and repeat" (with leading/trailing quotes)

### Usage

- Make a GET request to the `/search` endpoint with the `main_muscle` query parameter to search for exercises targeting a specific muscle group.
- Partial matches are supported. For example, searching for `Deltoid` will return exercises targeting "Deltoid", "Lateral Deltoid", "Anterior Deltoid", etc.

### Example Usage

#### Curl Command
```bash
curl "http://127.0.0.1:5000/search?main_muscle=Deltoid"
```

#### Postman
1. Open Postman.
2. Set the request type to `GET`.
3. Enter the URL `http://127.0.0.1:5000/search`.
4. Add a query parameter `main_muscle` with the value you want to search for.
5. Send the request.

This documentation provides all the necessary information to use the API effectively, including the full list of possible muscle groups you can search for.