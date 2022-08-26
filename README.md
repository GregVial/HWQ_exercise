# Instructions

## Background
You are provided part of the HWQ API that is used to send data from the HWQ device to the cloud. The device sends consumptions data (how much water was consummed, what were the start and end time, what was the water temperature etc).
The API is built with Python based on FastAPI framework and uses sqlite as database.

The code provided runs properly and has the following endpoints:
- ping: to check that the server is up and running, it allows 
- read_consumptions: to query existing consumptions data 
- create_consumptions: to create new ones, based on various criteria

## Objective
Create a new API end point that will enable query of the database between two dates, instead of the whole database.
If from date is empty, then start from the beginning of the database history.
If to date is emoty, then search until the current date.
If both dates are empty, search the entire database.
The query should be based on a board and circuit in addition to the date.
The purpose is to search inputs for a reduced timerange to reduce load on the server.

You should test the API with data you created by yourself.

Bonus: your API handles time zones, so you can specify in which time zone you are searching which will correctly translate into the unix timestamp.

## Expected result
Please send us your code back by email

## How to run the code provided

1. Install requirements.txt
2. Run the command from your shell ```uvicorn main:app --root-path="/"```
3. Open your browser at http://127.0.0.1:8000/docs
4. Run once the command "Read consumptions" (Try it out -> execute) to create the sqlite table. It should return an empty list
5. Create some entries in the database using "Create consumptions", using this example as a basis, you should receive an HTTP 201 answer
```{
  "boardId": "test",
  "millisBoard": 1661500348000,
  "tempC": 55,
  "tempM": 38,
  "tempF": 10,
  "mainLiters": 1,
  "circuits": [
    {
      "circuitId": 0,
      "timeStart": 1661500300000,
      "timeEnd": 16615000330000,
      "liters": 1.1,
      "litersF": 2.5
    }
  ]
}
```

Details about the json data:
- boardID: the id of the device
- millisBoard: the unix time in milliseconds when the data was actually send by the board
- tempC: hot water temperature, in degrees celsius
- tempM: engine temperature, in degrees celsius
- tempF: cold water temperature, in degrees celsius
- mainLiters: total liters of hot water consummed on board
- circuitId: the id of the circuit (appartement) that consummed water
- timeStart: the unix time in milliseconds when the water consumption started (should be lower than timeEnd)
- timeEnd: the unix time in milliseconds when the water consumption ended (should be lower than millisBoard)
- liters: quantity of hot water consummed during this session in liters
- litersF: quantity of cold water consummed during this session in liters

For your tests, the values that really matter are *boardID, millisBoard, circuitId, timeStart, timeEnd, liters*
Other values can be left with default value.


6. Check that the Read consumptions command returns the entry you just created