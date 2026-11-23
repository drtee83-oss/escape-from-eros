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
# GAME SETUP - Persistent values and AI prompt
# ================================================================

if "gameStarted" not in st.session_state:
    st.session_state.gameStarted = False

def startGame(name):
    st.session_state.gameStarted = True
    st.session_state.playerName = name
    st.session_state.health = 100
    st.session_state.healthMax = 100
    st.session_state.inventory = ["Pistol"]
    st.session_state.zones = ["docks1", "casino1", "hotel", "residential", "casino2",
        "warehouse", "docks2"]
    st.session_state.zoneNumber = 0
    st.session_state.resultType = ""
    st.session_state.resultMessage = ""
    st.session_state.resultValue = ""
    st.session_state.actionComplete = False
    st.session_state.noodles = False
    st.session_state.terminal = False
    st.session_state.radDamageApplied = False
    st.session_state.radDamage = 0

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
# Temporarily disabled AI for testing
    return fallback
#     if client == None:
#         return fallback


#     inventoryText = ", ".join(st.session_state.inventory)

#     prompt = f"""
# You are telling a story of how a disgraced Ceres detective travels to Eros (a space station in a mined out asteroid) to find a girl called Julie Mao. The case of Julie Mao, a rich Earther girl who joined the radical Belter faction, the OPA (Outer Planets Alliance), was given to him by his boss but he was told to let it go and then was fired when he didn't. The backdrop is The Expanse (book series by James SA Corey.)
 
# Player: {st.session_state.playerName}
# Room: {zone}
# Health: {st.session_state.health}/{st.session_state.healthMax}
# Inventory: {inventoryText}
 
# Action:
# {action}
 
# Outcome:
# {outcome}
 
# Describe what happens in 30-50 words.
 
# Use second person.
# Use gritty sci-fi language.
# Do not change the outcome.
# Do not change health or inventory.
# Do not introduce new choices.
# """
#     try:
#         interaction = client.interactions.create(
#             model="gemini-3.5-flash-lite",
#             input=prompt,
#             generation_config={"thinking_level": "minimal"}
#         )
#         if interaction.output_text:
#             return interaction.output_text
#         return fallback
#     except Exception as error:
#         st.error(f"Gemini error: {error}")
#         return fallback

def rng():
    return random.randint(1,6)

def chanceEncounter(buttonText, zone, action, successNumber, successOutcome, successFallback, failureOutcome, failureFallback, damage, bonusItem ="", successItem="", bonusFlag=""):
    if st.button(buttonText):
        roll = rng()
        if bonusItem != "" and itemCheck(bonusItem):
            roll = roll + 2
        if bonusFlag != "" and st.session_state[bonusFlag]:
            roll += 2
        if roll >= successNumber:
            if successItem != "":
                itemAdd(successItem)
            story = generateStory(zone, action, successOutcome, successFallback)
            setResult("success", story)
        else:
            takeDamage(damage)
            story = generateStory(zone, action, failureOutcome, failureFallback)
            setResult("damage", story, damage)
        st.rerun()

# ================================================================
# REUSABLE FUNCTIONS - Text and interactive elements
# ================================================================

def showZone(title, description):
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
        f"Zone {st.session_state.zoneNumber + 1} "
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

def resetAction():
    st.session_state.resultType = ""
    st.session_state.resultMessage = ""
    st.session_state.resultValue = ""
    st.session_state.actionComplete = False
    st.rerun()

# ================================================================
# START SCREEN - Arrival at Eros docks
# ================================================================

if not st.session_state.gameStarted:
    st.write("You disembark the ship, glad to leave the cramped, hot cabin of the ancient passenger transport. As you step onto the docks of another world, you gaze around, heedless of the other arrivals pushing past you. 'Not all the different from Ceres...', you muse.")
    name = st.text_input("An immigration officer saunters over, a sly smile on his face as he asks you for your ID. 'So, who do we got here, beratna?', he asks in a thick Belter accent.")
 
    if st.button("Present ID and enter Eros Station"):
        if name.strip():
            startGame(name)
            st.rerun()
        else:
            st.warning("'Don't sound like no name I ever heard of. Wanna run that by me again?', the immigration officer asks.")
else:
    # Show the same player information on every room.
    showPlayerInfo()
    zone = getCurrentZone()

    if st.session_state.health <= 0:
        showZone("💀 You Died", "As the last of your strength ebbs, you fatalistically mumble, 'some you win, some you lose...'")
        st.error("Mission failed...")
        if st.button("🔄 Retry?"):
            restartGame()
        st.stop()

    # ================================================================
    # ZONE 1 - Eros Docking Ring, Sematimba meeting
    # ================================================================
    if zone == "docks1":
        showZone(f"🚀 Eros Docking Ring", "You stroll past the immigration officer, still gawking at your surroundings. You hear a familar voice ring out, 'there you are, you old fraud! Were you gonna walk on by without saying hi to an old friend?'")
        showContinueButton("🚶‍➡️ Greet your old buddy")

    # ================================================================
    # ZONE 2 - Casino level 1, noodle cart
    # ================================================================

    elif zone == "casino1":
        showZone("🕯️ Casino Level", "A riot of sound and colour assault your senses as you step into one of Eros' three famed casino levels. Your old friend, Sematimba, all but drags you to a noodle cart. 'Try the soba! Best in the belt!', he claims enthusiastically.")
        if not st.session_state.actionComplete:
            left, right = st.columns(2)
            with left:
                if st.button("🍜 Sit and eat"):
                    st.session_state.noodles = True
                    story = generateStory(
                        "Casino Level", 
                        "the player sits down with Sematimba, a cop on Eros, to eat noodles and trade war stories about the interjurisdictional case they worked together while the player was a detective on Ceres", 
                        "The player is happy to have seen and reconnected with a friendly face and Sematimba says to the player that if they need a hand while they're on Eros, to reach out to him.", 
                        "You sit at the grimy noodle cart and order the same as Sematimba. As you eat, you reminisce about a case you both worked together. As you finish up and stand up to move on, Sematimba claps your shoulder. 'You need a hand while you're here, you know where to find me.'"
                        )
                    setResult("story", story)
            with right:
                if st.button("🙂‍↔️ Decline the invitation"):
                    st.session_state.noodles = False
                    story = generateStory(
                        "Casino Level", 
                        "the player decides not to accept the invitation, instead moving on as they're in a rush", 
                        "You briefly clasp Sematimba's shoulder and say 'some other time, buddy' before hurrying off towards the nearest vac-tube station.", 
                        "'Sorry, buddy', you say, 'in a hell of a rush right now. Rain check?' 'Sure thing...', a bemused Sematimba says, watching you stride on towards the nearest vac-tube station."
                        )
                    setResult("story", story)
        else:
            showResult()
            showContinueButton("🚅 Board the vac-tube to the residential level")

    # ================================================================
    # ZONE 3 - Hotel level, find Julie Mao
    # ================================================================

    elif zone == "hotel":
        showZone("🏩 Blue Falcon Hotel", f"You exit the vac-tube into a dingy tunnel. A feeble blue sign reading 'BLUE FALCON HOTEL' is barely visible 200 metres spinward. As you approach the entrance, you realise that 'hotel' is a grandiose claim for what is little more than a flophouse. \nYou walk through the door anyway, a sense of unease starting to trail its fingers down your spine. There's not much to see, just a busted old vending machine, a couple of old couches (on one of which is a shifty middle-aged woman reading a magazine), and an info terminal. \nThe staircase to the rooms is on your right.")
        if not st.session_state.actionComplete:
            left, right = st.columns(2)
            with left:
                if st.button("🖥️ Access the terminal"):
                    st.session_state.terminal = True
                    story = generateStory(
                        "Hotel/flophouse called The Blue Falcon Hotel",
                        "The player checks the room listings on the terminal and spots 'Lionel Polanski', a known alias of Julie Mao, in room 25.",
                        "The player notes the room number down and turns to head up the stairs",
                        "You swipe through the list of guests and find Lionel Polanski, a known alias of Julie Mao, in room 25. You make a mental note of the room number and turn towards the stairs."
                    )
                    setResult("success", story)
            with right:
                if st.button("🪜 Climb the stairs"):
                    if st.session_state.terminal:
                        story = generateStory(
                            "Hotel/flophouse called The Blue Falcon Hotel",
                            "The player checks the room listings on the terminal and spots 'Lionel Polanski', a known alias of Julie Mao, in room 25.",
                            "The player notes the room number down and heads up the stairs to find it. Upon entering the room, they find Julie Mao dead in the shower, her corpse infected with some kind of glowing blue organism. All electronic devices in the room have been destroyed.",
                            "You apprehensively climb the stairs and find room 25. As you enter, a rotting smell assails your nostrils. You notice that the light switch doesn't work and there isn't the usual glow of electronics. You find Julie in the shower, dead and infected by a glowing blue organism of some kind."
                    )
                        setResult("success", story)
                    else:
                        story = generateStory(
                            "Hotel/flophouse called The Blue Falcon Hotel",
                            "The player goes straight up the stairs and picks a random, wrong room number between 20 and 30 but not 25.",
                            "The player knocks on the wrong door and a cantankerous old man shouts at him for disturbing his meal. The player decides to return to the lobby to check the terminal.",
                            "You realise you don't know which room Julie is in so you pick one at random and knock on the door. An old man in a stained bathrobe opens it. 'WHADAYOOWANT?!', he yells, 'CAN'T A GUY HAVE DINNER IN PEACE?!' He slams the door but you still hear him muttering obscenities through the flimsy material."
                        )
                        setResult("story", story)
        else:
            showResult()
            if st.session_state.resultType == "success":
                showContinueButton("Continue")
            else:
                if st.button("↩️ Return to the lobby"):
                    resetAction()

    # ================================================================
    # ZONE 4 - Residential tunnel, shootout with mercs
    # ================================================================

    elif zone == "residential":
        showZone("➡️ Residential Tunnel", "You exit the hotel back into the tunnel. You are ambushed by mercenaries in body armour toting rifles. You take cover in the doorway of a nearby pachinko parlour.")
        if not st.session_state.actionComplete:
            chanceEncounter(
                "🔫 Fire at the mercenaries",
                "Blue Falcon Hotel",
                "The player engages a pair of armed mercs in a firefight. If the player ate noodles with Sematimba earlier, he provides backup.",
                4,
                "You fell both attackers!",
                "You return fire, ducking in and out of the doorway between shots. Both attackers are finally downed and the coast is clear!",
                "The player is wounded during the firefight but survives.",
                "You exchange fire with the mercs, but one of them wings you. You fire a couple more shots, driving them back into cover.",
                20,
                bonusFlag="noodles"
            )
        else:
            showResult()
            if st.session_state.resultType == "success":
                showContinueButton("Continue")
            else:
                chanceEncounter(
                    "🔫 Fire again!",
                    "Blue Falcon Hotel",
                    "The player continues to exchange fire with the mercenaries.",
                    4,
                    "You fell both attackers!",
                    "You return fire, still ducking in and out of cover. Both attackers are finally downed and the coast is clear!",
                    "The player takes another graze from a bullet.",
                    "Another bullet grazes you. Your breath it starting to come in ragged gasps but you keep on fighting.",
                    20,
                    bonusFlag="noodles"
                )

    # ================================================================
    # ZONE 5 - Casino level 2, rad shelter incident
    # ================================================================

    elif zone == "casino2":
        showZone("➡️ Casino Level", "The coast clear, you head down the ramp back to the Casino Level. As you walk, you hear a loud klaxon and an announcement on the PA system: 'Citizens of Eros, there has been an uncontained engine explosion in docking bay D74. As a precaution, all citizens are advised to head to the nearest hard radiation shelter. Officers will be on hand to guide you. There is no need for panic so please proceed in a calm and orderley manner.' You see a guard near a tall metal door ushering nervous citizens into one of the shelters. You head over just as a blinding flash of searing white light slams into your retinas. Your hand terminal buzzes furiously, telling you that you have just received a lethal dose of gamma radiation.")

        if not st.session_state.radDamageApplied:
            damage = random.choice([30, 40, 50, 60])
            takeDamage(damage)
            st.session_state.radDamageApplied = True
            st.session_state.radDamage = damage

            st.rerun()

        if not st.session_state.actionComplete:
            st.error(
                f"☢️ Exposed to high energy gamma radiation. You lose {st.session_state.radDamage} health!"
            )

            st.write(
                "You stumble, still half blinded and suddenly weary. You notice a clinic across the tunnel. Maybe they have meds that can alleviate the symptons long enough for you to get off this rock."
            )
            left, right = st.columns(2)
            with left:
                if st.button("🏥 Stumble towards the clinic"):
                    itemAdd("Anti-Rad Meds")
                    story = generateStory(
                        "Casino level medical clinic",
                        "The player stumbles into the clinic seeking medicine for radiation exposure",
                        "The player find some anti-radiation medicine and pockets it.",
                        "You stagger into the clinic and see some anti-radiation medicine on the counter. You breathe a sigh of relief as you pocket the syringe.",
                    )
                    setResult("item", story, "Anti-rad Meds")

            with right:
                if st.button("➡️ Keep moving"):
                    story = generateStory(
                        "Casino level",
                        "The player ignores the clinic and presses onwards",
                        "The player decides to move on despite the radiation sickness",
                        "You decide that time is of the essence and hurry on towards the docks.",
                    )

                    setResult("success", story)

        else:
            showResult()

            if itemCheck("Anti-Rad Medication"):

                if st.button("💊 Administer anti-rad medication"):

                    restored = restoreHealth(50)
                    itemRemove("Anti-Rad Medication")

                    story = generateStory(
                        "Casino level",
                        "The player administers anti-radiation medication.",
                        f"The player recovers {restored} health.",
                        "You take the anti-radiation medication. Gradually, "
                        "the nausea begins to subside and you feel stronger."
                    )

                    setResult("heal", story, restored)

            showContinueButton("Continue")

# ================================================================
# ZONE 6 - Warehouse level, second merc encounter
# ================================================================

    elif zone == "warehouse":
        showZone("➡️ Warehouse Level", "You make your way out of the casino level and find yourself in the warehouse level. You breathe a sigh of relief: this level has direct access to the docks. As you shuffle onwards, you see two mercs arguing ahead and quickly drop down behind a nearby crate. You have two choices: fight or find an alternative route.")

        if itemCheck("Anti-Rad Meds"):

            if st.button("💊 Administer anti-rad medication"):

                restored = restoreHealth(50)
                itemRemove("Anti-Rad Meds")

                story = generateStory(
                    "Warehouse level",
                    "The player takes their anti-radiation medication.",
                    f"The player recovers {restored} health.",
                    "You swallow the anti-radiation medication. "
                    "Gradually, you begin to feel a little stronger."
                )

                setResult("heal", story, restored)

        if not st.session_state.actionComplete:
            left, right = st.columns(2)
            with left:
                chanceEncounter(
                    "🔫 Fire at the mercs",
                    "Warehouse level",
                    "The player engages two armed mercenaries in a firefight. The player has the element of surprise.",
                    4,
                    "The player defeats both enemies and takes one of their sets of body armour",
                    "You rapidly fire two shots at the mercenaries, aiming at the weak spot between the helmet and the shoulder pads. Both of them drop to the ground and you strip one of them of their armour.",
                    "The player misses one of his shots, alerting the mercs to his presence and takes a bullet in the process, becoming wounded.",
                    "Your first shot hits but your second only wings the target. The element of surprise lost, they manage to get a shot in before you dive back behind the crate, wounding you.",
                    20,
                    successItem="Mercenary Armour"
                )
            with right:
                if st.button("🏃‍➡️ Find another route"):
                    story = generateStory(
                        "Warehouse level",
                        "The player softly retraces his steps, opting for another route to the docks.",
                        "The player avoids the fight but doesn't acquire the armour.",
                        "You feel too weak to be confident in your chances against two armed and armoured opponents so you softly retrace your steps and try to find another route to the docks."
                    )

                    setResult("success", story)

        else:
            showResult()

            if st.session_state.resultType == "success":
                showContinueButton("Continue")
            else:
                left, right = st.columns(2)

                with left:
                    chanceEncounter(
                    "🔫 Fire again!",
                    "Warehouse level",
                    "The player continues to engage the two armed mercenaries, the element of surprise now lost.",
                    4,
                    "The player defeats both enemies and takes one of their sets of body armour",
                    "You pop out of cover, quickly firing off a volley shots. Both mercs are now down and you strip one of them of their armour.",
                    "The player is wounded again.",
                    "Your salvo misses the mark and you are caught by another bullet, further wounding you.",
                    20,
                    successItem="Mercenary Armour"
                    )

                with right:
                    if st.button("🏃‍➡️ Find another route"):
                        story = generateStory(
                            "Warehouse level",
                            "The player abandons the fight and flees down a side corridor to find a different route to the docks.",
                            "The player escapes but does not acquire the mercenary armour.",
                            "You feel your strength ebbing so you use what little of it you have left to retreat into a side corridor hoping to find an alternate route. You hear the mercs laughing obnoxiously behind you but they do not give chase."
                        )
                        setResult=("success", story)