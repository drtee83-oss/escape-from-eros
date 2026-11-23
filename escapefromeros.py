import os
import streamlit as st
import random
from dotenv import load_dotenv
from google import genai
 
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
 
client = genai.Client(api_key=api_key) if api_key else None
 
MODEL_NAME = "gemini-3.5-flash-lite"

# ================================================================
# PAGE SETUP - Page title, favicon
# ================================================================

st.set_page_config(page_title="Escape from Eros", page_icon="🚀", layout="centered")
st.title("🚀 ESCAPE FROM EROS 🚀")

# ================================================================
# GAME SETUP - PERSISTENT VARIABLES AND AI PROMPT
# ================================================================

if "gameStarted" not in st.session_state:
    st.session_state.gameStarted = False

def startGame(name):
    st.session_state.gameStarted = True
    st.session_state.playerName = name
    st.session_state.health = 100
    st.session_state.healthMax = 100
    st.session_state.inventory = ["Pistol"]
    st.session_state.zones = ["docks1", "casino1", "hotel", "casino2",
        "warehouse", "docks2"]
    st.session_state.zoneNumber = 0
    st.session_state.resultType = ""
    st.session_state.resultMessage = ""
    st.session_state.resultValue = ""
    st.session_state.actionComplete = False
    st.session_state.noodles = False
    st.session_state.terminal - False

def restartGame():
    st.session_state.clear()
    st.rerun()
 
def getCurrentZone():
    return st.session_state.zones[st.session_state.zoneNumber]
 
def continueGame():
    st.session_state.resultType = ""
    st.session_state.resultMessage = ""
    st.session_state.resultValue = ""
    st.session_state.actionComplete = False
    st.session_state.zoneNumber += 1
    st.rerun()

def itemAdd(item):
    if item not in st.session_state.inventory:
        st.session_state.inventory.append(item)

def itemCheck(item):
    return item in st.session_state.inventory

def itemRemove(item):
    if item in st.session_state.inventory:
        st.session_state.inventory.remove(item)

def takeDamage(amount):
    st.session_state.health -= amount
    if st.session_state.health < 0:
        st.session_state.health = 0

def restoreHealth(amount):
    healthOld = st.session_state.health
    st.session_state.health = min(st.session_state.healthMax, st.session_state.health + amount)
    return st.session_state.health - healthOld

def generateStory(zone, action, outcome, fallback):
    if client == None:
        return fallback


    inventoryText = ", ".join(st.session_state.inventory)

    prompt = f"""
You are telling a story of how a disgraced Ceres detective travels to Eros (a space station in a mined out asteroid) to find a girl called Julie Mao. The case of Julie Mao was given to him by his boss but he was told to let it go and then was fired when he didn't. The backdrop is The Expanse (book series by James SA Corey.)
 
Player: {st.session_state.playerName}
Room: {zone}
Health: {st.session_state.health}/{st.session_state.healthMax}
Inventory: {inventoryText}
 
Action:
{action}
 
Outcome:
{outcome}
 
Describe what happens in 30-50 words.
 
Use second person.
Use gritty sci-fi language.
Do not change the outcome.
Do not change health or inventory.
Do not introduce new choices.
"""
    try:
        interaction = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=prompt,
            generation_config={"thinking_level": "minimal"}
        )
        if interaction.output_text:
            return interaction.output_text
        return fallback
    except Exception as error:
        st.error(f"Gemini error: {error}")
        return fallback

def rng():
    return random.randint(1,6)

def chanceEncounter(buttonText, zone, action, successNumber, successOutcome, successFallback, failureOutcome, failureFallback, damage, bonusItem ="", successItem=""):
    if st.button(buttonText):
        roll = rng()
        if bonusItem != "" and itemCheck(bonusItem):
            roll = roll + 2
        if roll >= successNumber:
            story = generateStory(zone, action, successOutcome, successFallback)
            setResult("success", story)
        else:
            takeDamage(damage)
            story = generateStory(zone, action, failureOutcome, failureFallback)
            setResult("damage", story, damage)
        st.rerun()

# ================================================================
# REUSABLE FUNCTIONS
# ================================================================

def showRoom(title, description):
    st.header(title)
    st.write(description)
 
def showPlayerInfo():
    st.subheader(f"🧑 {st.session_state.playerName} ")
    left, right = st.columns(2)
    with left:
        st.write(f"❤️ Health: {st.session_state.health} / {st.session_state.healthMax}")
    with right:
        st.write(f"🎒 Inventory: {', '.join(st.session_state.inventory)}")  
    st.caption(
        f"Room {st.session_state.zoneNumber + 1} "
        f"of {len(st.session_state.zones)}"
    )
    st.divider()

def setResult(resultType, message, value=""):
    st.session_state.resultType = resultType
    st.session_state.resultMessage = message
    st.session_state.resultValue = value
    st.session_state.actionComplete = True
    st.rerun()
 
def showResult():
    kind = st.session_state.resultType
    value = st.session_state.resultValue
 
    if kind == "item":
        st.success(f"🎒 NEW ITEM: {value}")
    elif kind == "damage":
        st.error(f"💔 DAMAGE: You lose {value} health.")
    elif kind == "heal":
        st.success(f"💚 HEALED: You recover {value} health.")
    elif kind == "success":
        st.success("✅ Success!")
    else:
        st.info("The journey continues...")
 
    st.write(st.session_state.resultMessage)
 
def showContinueButton(text = "Continue"):
    if st.button(text):
        continueGame()