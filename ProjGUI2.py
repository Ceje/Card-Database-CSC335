import Tkinter
import MySQLdb


def connect(userID, password):
    global con
    global cur
    global uID
    con.close()
    cur.close()
    con= MySQLdb.connect(host= "Infectionserver.no-ip.org",
                          port= 3307,
                          user= userID,
                          passwd= password,
                          db = "CSC335")
    cur=con.cursor()
    cur.execute("select user_ID from users where name='"+user+"';")
    uID=int(cur.fetchone()[0])
    return con

def conn(userID):#only used for initial database panel
    conn= MySQLdb.connect(host= "Infectionserver.no-ip.org",
                          port= 3307,
                          user= userID,
                          db = "CSC335")
    return conn

class databasePanel:
    def __init__(self, frameL):
        self.search = LabelFrame(frameL,text="search")
        self.search.pack(fill=X)
        self.sIn= Entry(self.search)
        self.sIn.pack(fill=X)
        self.searchButton = Button(self.search, text="go", command=self.updateSearch)
        self.searchButton.pack(fill=X)
        #DATABASE LIST
        self.database = LabelFrame(frameL, text="Database")
        self.database.pack(fill=X)
        self.scrollbarL = Scrollbar(self.database)
        

        self.mylistL = Listbox(self.database, yscrollcommand = self.scrollbarL.set, selectmode=SINGLE)
        cur.execute("select name, ed_index from card;")
        self.dataList =cur.fetchall()
        for line in self.dataList:
           self.mylistL.insert(END, line)
        #CARDVIEW TEXT
        self.cardview= LabelFrame(frameL, text="cardview")
        self.cardview.pack(fill=X)

        self.mylistL.pack( side = LEFT, fill = BOTH )
        self.scrollbarL.pack( side = LEFT, fill=Y )
        #select button
        self.cardupdatebutton=Button(self.database, text="select",command=self.updateCard)
        self.scrollbarL.config( command = self.mylistL.yview )
        self.cardupdatebutton.pack()
        
        self.card = Label(self.cardview,text="")
        self.card.pack(fill=Y)

    def updateSearch(self):
        self.mylistL.delete(0,self.mylistL.size())
        #get search results from server and store in newList
        cur.execute("select name, ed_index from card where name ='"+self.sIn.get()+"'")
        newList=cur.fetchall()
        for x in newList:
            self.mylistL.insert(END,x)

    def updateCard(self):
        self.sel=self.mylistL.curselection()
        #print(self.sel)
        #print(self.mylistL.get(self.sel))
        cur.execute("select name, ed_index, mainType, subType, attack, defense from card where name='"+self.mylistL.get(self.sel)[0]+"' and ed_index='"+self.mylistL.get(self.sel)[1]+"';")
        self.Cdata=cur.fetchone()
        self.card.config(text=self.Cdata)

    def refresh(self):
        self.mylistL.delete(0,END)
        cur.execute("select name, ed_index from card")
        newList=cur.fetchall()
        for x in newList:
            self.mylistL.insert(END,x)
            
class collectionPanel:
    def __init__(self, frameR):
        self.colV=LabelFrame(frameR, text="collection")
        self.colV.pack()
        self.scrollbarR = Scrollbar(self.colV)
        
        #card collection menu
        self.mylistR = Listbox(self.colV, yscrollcommand = self.scrollbarR.set )
        cur.execute("select card_name, ed_index, number from cards_owned where user_ID='"+str(uID)+"';")
        self.dataList=cur.fetchall()
        for line in self.dataList:
           self.mylistR.insert(END, line)

        self.mylistR.pack( side = LEFT, fill = BOTH )
        self.scrollbarR.pack( side = LEFT, fill=Y )
        self.scrollbarR.config( command = self.mylistR.yview )
        self.buttons=Frame(self.colV)
        self.buttons.pack(side=LEFT,fill=Y)
        self.addC=Button(self.buttons, text="add Card", command=lambda:self.addCard)
        self.remC=Button(self.buttons, text="remove Card",command=lambda:self.removeCard())
        self.selC=Button(self.buttons, text="select",command=lambda:self.updateCard)
        self.addC.pack(fill=X)
        self.remC.pack(fill=X)
        self.selC.pack(fill=X)
        
    def hide(self):
        self.colV.pack_forget()

    def show(self):
        self.colV.pack()

    def updateCard(self, databasePanel):
        self.sel=self.mylistR.curselection()
        #print(self.sel)
        #print(self.mylistL.get(self.sel))
        cur.execute("select name, ed_index, mainType, subType, attack, defense from card where name='"+self.mylistR.get(self.sel)[0]+"' and ed_index='"+self.mylistR.get(self.sel)[1]+"';")
        databasePanel.Cdata=cur.fetchone()
        databasePanel.card.config(text=databasePanel.Cdata)

    def addCard(self, databasePanel):
        searchKey=databasePanel.mylistL.get(databasePanel.mylistL.curselection())
        cur.execute("select number from cards_owned where card_name='"+searchKey[0]+"' and user_ID="+str(uID)+" and ed_index='"+searchKey[1]+"';")
        count=cur.fetchone()
        if count:
            count=int(count[0])+1
            cur.execute("UPDATE cards_owned SET number="+str(count)+" WHERE card_name='"+searchKey[0]+"' and user_ID="+str(uID)+" and ed_index='"+searchKey[1]+"';")
        else:
            cur.execute("INSERT INTO cards_owned(user_ID, card_name, ed_index, number) VALUES("+str(uID)+",'"+searchKey[0]+"', '"+searchKey[1]+"', 1);")
        con.commit()
        self.refresh()

    def removeCard(self):
        searchKey=self.mylistR.get(self.mylistR.curselection())
        cur.execute("select number from cards_owned where card_name='"+searchKey[0]+"' and user_ID="+str(uID)+" and ed_index='"+searchKey[1]+"';")
        count=int(cur.fetchone()[0])
        if count>1:
            count=count-1
            cur.execute("UPDATE cards_owned SET number="+str(count)+" WHERE card_name='"+searchKey[0]+"' and user_ID="+str(uID)+" and ed_index='"+searchKey[1]+"';")
        else:
            cur.execute("DELETE FROM cards_owned WHERE card_name='"+searchKey[0]+"' and user_ID="+str(uID)+" and ed_index='"+searchKey[1]+"';")
        con.commit()
        self.refresh()
        
    def refresh(self):
        self.mylistR.delete(0,END)
        cur.execute("select card_name,ed_index,number  from cards_owned where user_ID="+str(uID)+";")
        self.dataList=cur.fetchall()
        for line in self.dataList:
           self.mylistR.insert(END, line)
    
class deckPanel:
    def __init__(self,frameR):
        self.deckV=LabelFrame(frameR, text="deck")
        self.deckV.pack(side=LEFT)
        
        #deck selection menu
        self.deckScroll = Scrollbar(self.deckV)
        self.deckScroll.pack( side = LEFT, fill=Y )
        self.deckList = Listbox(self.deckV, yscrollcommand = self.deckScroll.set )
        cur.execute("select deck_name from owned_decks where user_ID='"+str(uID)+"';")
        self.dataList=cur.fetchall()
        for line in self.dataList:
           self.deckList.insert(END, line[0])

        self.deckList.pack( side = LEFT, fill = BOTH )
        self.deckScroll.config( command = self.deckList.yview )

        #deck display menu
        self.dcScroll=Scrollbar(self.deckV)
        self.dcList = Listbox(self.deckV, yscrollcommand = self.dcScroll.set)
        self.dcList.pack(side=LEFT,fill=BOTH)
        self.dcScroll.pack(side=LEFT,fill=Y)
        self.dcScroll.config(command=self.dcList.yview)
        self.buttons=Frame(self.deckV)
        self.buttons.pack(side=LEFT,fill=Y)
        self.addC=Button(self.buttons, text="add Card", command=lambda:self.addCard)
        self.remC=Button(self.buttons, text="remove Card",command=lambda:self.removeCard())
        self.selC=Button(self.buttons, text="select",command=lambda:self.updateCard)
        self.addD=Button(self.buttons, text="new Deck", command=lambda:self.addDeck())
        self.remD=Button(self.buttons, text="delete Deck", command=lambda:self.removeDeck())
        self.selD=Button(self.buttons, text="select Deck", command=lambda:self.selDeck())
        self.deckName=LabelFrame(self.buttons, text="Deck Name")
        self.newD=Entry(self.deckName)
        self.addC.pack(fill=X)
        self.remC.pack(fill=X)
        self.selC.pack(fill=X)
        self.deckName.pack(fill=X)
        self.newD.pack(fill=X)
        self.addD.pack(fill=X)
        self.remD.pack(fill=X)
        self.selD.pack(fill=X)
        
    def hide(self):
        self.deckV.pack_forget()

    def show(self):
        self.deckV.pack()

    def updateCard(self, databasePanel):
        self.sel=self.dcList.curselection()
        #print(self.sel)
        #print(self.mylistL.get(self.sel))
        cur.execute("select name,ed_index, mainType, subType, attack, defense from card where name='"+self.dcList.get(self.sel)[0]+"' and ed_index='"+self.dcList.get(self.sel)[1]+"';")
        databasePanel.Cdata=cur.fetchone()
        databasePanel.card.config(text=databasePanel.Cdata)

    def addCard(self, databasePanel):
        searchKey=str(databasePanel.mylistL.get(databasePanel.mylistL.curselection())[0])
        cur.execute("select number from deck where card_name='"+searchKey+"' and deck_ID="+str(deckID)+";")
        count=cur.fetchone()
        if count:
            count=int(count[0])+1
            cur.execute("UPDATE deck SET number="+str(count)+" WHERE card_name='"+searchKey+"' and deck_ID="+str(deckID)+";")

        else:
            cur.execute("INSERT INTO deck(deck_ID, card_name, number, ed_index) VALUES ("+str(deckID)+",'"+searchKey+"', 1, '"+databasePanel.mylistL.get(databasePanel.mylistL.curselection())[1]+"');")
        con.commit()
        self.refreshD()
        
    def removeCard(self):
        searchKey=str(self.dcList.get(self.dcList.curselection())[0])
        cur.execute("select number from deck where card_name='"+searchKey+"' and deck_ID="+str(deckID)+";")
        count=int(cur.fetchone()[0])
        if count>1:
            count=count-1
            cur.execute("UPDATE deck SET number="+str(count)+" WHERE card_name='"+searchKey+"' and deck_ID="+str(deckID)+";")
        else:
            cur.execute("DELETE FROM deck WHERE card_name='"+searchKey+"' and deck_ID="+str(deckID)+";")
        con.commit()
        self.refreshD()
        
    def selDeck(self):
        global deckID
        searchKey=str(self.deckList.get(self.deckList.curselection())[0])
        self.dcList.delete(0,END)
        cur.execute("select deck_ID from owned_decks where deck_name='"+searchKey+"';")
        deckID=int(cur.fetchone()[0])
        cur.execute("select card_name, ed_index, number from deck where deck_ID="+str(deckID)+";")
        self.deckData=cur.fetchall()
        for x in self.deckData:
            self.dcList.insert(END,x)
    
    def addDeck(self):
        cur.execute("INSERT INTO owned_decks(user_ID, deck_name) VALUES("+str(uID)+",'"+self.newD.get()+"');")
        con.commit()
        self.refresh()
        
    def removeDeck(self):
        cur.execute("DELETE FROM deck where deck_ID="+str(deckID)+";")
        cur.execute("DELETE FROM owned_decks where deck_ID="+str(deckID)+";")
        con.commit()
        self.refresh()
        self.refreshD()
        
    def refresh(self):
        global deckID
        deckID=''
        cur.execute("select deck_name from owned_decks where user_ID='"+str(uID)+"';")
        self.dataList=cur.fetchall()
        self.deckList.delete(0,END)
        self.dcList.delete(0,END)
        for line in self.dataList:
            self.deckList.insert(END, line)
            
    def refreshD(self):
        cur.execute("select card_name, ed_index, number from deck where deck_ID='"+str(deckID)+"'")
        self.dcList.delete(0,END)
        self.deckData=cur.fetchall()
        for x in self.deckData:
            self.dcList.insert(END,x) 

class adminPanel:
    def __init__(self,frameR):
        self.admV=LabelFrame(frameR, text="admin")
        self.admV.pack()
        #creates user options
        self.tools=LabelFrame(self.admV, text="admin tools")
        self.tools.pack()
        
        self.users=Button(self.tools, text="user options", command=lambda: self.userO())
        self.users.pack(fill=X)
        self.userV=LabelFrame(self.tools, text="Users")
        self.userV.pack()
        self.userSB=Scrollbar(self.userV)
        self.userList= Listbox(self.userV,yscrollcommand = self.userSB.set )
        self.userSB.config( command = self.userList.yview )
        self.newUser= LabelFrame(self.userV, text="new user")
        self.userName= Entry(self.newUser)
        self.addU=Button(self.newUser, text="add User", command=lambda: self.adduser())
        self.delU=Button(self.userV, text="delete User", command=lambda: self.deluser())
        self.selU=Button(self.userV, text="select User", command=lambda: self.seluser())
        #displays user options
        self.userList.pack(side=LEFT, fill=BOTH)
        self.userSB.pack(side=LEFT,fill=Y)
        self.newUser.pack(fill=X)
        self.userName.pack(fill=X)
        self.addU.pack(fill=X)
        self.delU.pack(fill=X)
        self.selU.pack(fill=X)
        #removes user options
        self.userV.pack_forget()

        #creates card options
        self.cards=Button(self.tools, text="card options", command=lambda: self.cardO())
        self.cards.pack(fill=X)
        self.cardV=LabelFrame(self.tools, text="Cards")
        self.cardN=LabelFrame(self.cardV, text="new card")
        self.cName=Entry(self.cardN)
        self.cName.insert(0,"name")
        self.cEd=Entry(self.cardN)
        self.cEd.insert(0, "Edition")
        
        self.cCostR=Entry(self.cardN)
        self.cCostR.insert(0,"cost Red")
        self.cCostBu=Entry(self.cardN)
        self.cCostBu.insert(0,"cost Blue")
        self.cCostW=Entry(self.cardN)
        self.cCostW.insert(0,"cost White")
        self.cCostBa=Entry(self.cardN)
        self.cCostBa.insert(0,"cost Black")
        self.cCostG=Entry(self.cardN)
        self.cCostG.insert(0,"cost Green")
        self.cCost=Entry(self.cardN)
        self.cCost.insert(0,"cost colorless")
        self.cCostx=Entry(self.cardN)
        self.cCostx.insert(0,"cost X")
        self.cCosts=Entry(self.cardN)
        self.cCosts.insert(0,"cost special")
        self.cCostsv=Entry(self.cardN)
        self.cCostsv.insert(0,"cost special value")
        
        self.cStr=Entry(self.cardN)
        self.cStr.insert(0,"strength")
        self.cHP=Entry(self.cardN)
        self.cHP.insert(0, "life")
        self.cAbility=Entry(self.cardN)
        self.cAbility.insert(0,"Abilities")
        self.cFlavor=Entry(self.cardN)
        self.cFlavor.insert(0,"flavor")
        self.cRare=Entry(self.cardN)
        self.cRare.insert(0,"rarity")
        self.cT1=Entry(self.cardN)
        self.cT1.insert(0,"Type1")
        self.cT2=Entry(self.cardN)
        self.cT2.insert(0,"Type2")
        self.cEd=Entry(self.cardN)
        self.cEd.insert(0,"edition index")
        self.addC=Button(self.cardN, text="add Card")
        self.delC=Button(self.cardV, text="delete Card")
        
        self.cardV.pack(fill=X)
        self.cardN.pack(fill=X)
        #displays entry boxes
        self.cName.pack(fill=X)
        self.cEd.pack(fill=X)
        
        
        self.cCostR.pack(fill=X)
        self.cCostBu.pack(fill=X)
        self.cCostW.pack(fill=X)
        self.cCostBa.pack(fill=X)
        self.cCostG.pack(fill=X)
        self.cCost.pack(fill=X)
        self.cCostx.pack(fill=X)
        self.cCosts.pack(fill=X)
        self.cCostsv.pack(fill=X)
        
        self.cT1.pack(fill=X)
        self.cT2.pack(fill=X)
        self.cAbility.pack(fill=X)
        self.cFlavor.pack(fill=X)
        self.cRare.pack(fill=X)
        self.cStr.pack(fill=X)
        self.cHP.pack(fill=X)
        #displays buttons
        self.addC.pack(fill=X)
        self.delC.pack(fill=X)
        #removes card options
        self.cardV.pack_forget()
        #removes admin panel
    def hide(self):
        self.admV.pack_forget()

    def show(self):
        self.admV.pack()

    def cardO(self):
        self.userV.pack_forget()
        self.cardV.pack()

    def userO(self):
        self.cardV.pack_forget()
        self.userV.pack()

    def newCard(self, databasePanel):
        name=self.cName.get()
        edition=self.cEd.get()
        cRed=self.cCostR.get()
        cBlue=self.cCostBu.get()
        cWhite=self.cCostW.get()
        cBlack=self.cCostBa.get()
        cGreen=self.cCostG.get()
        cLess=self.cCost.get()
        cX=self.cCostx.get()
        cs=self.cCosts.get()
        csv=self.cCostsv.get()
        mType=self.cT1.get()
        sType=self.cT2.get()
        ef=self.cAbility.get()
        rare=self.cRare.get()
        atk=self.cStr.get()
        hp=self.cHP.get()
        cur.execute("INSERT INTO card(name,ed_index,cost_Red,cost_Blue,cost_White,cost_Black,cost_Green,cost_colorless,var_colorless,var_special,cost_special,mainType,subType,effect,rarity,attack,defense) Values ('"+name+"','"+edition+"',"+cRed+","+cBlue+","+cWhite+","+cBlack+","+cGreen+","+cLess+","+cX+",'"+cs+"',"+csv+",'"+mType+"','"+sType+"','"+ef+"','"+rare+"','"+atk+"','"+hp+"');")
        con.commit()
        databasePanel.refresh()
        
    def delCard(self, databasePanel):
        searchKey=databasePanel.mylistL.get(databasePanel.mylistL.curselection())
        cur.execute("DELETE FROM deck WHERE card_name='"+searchKey[0]+"' and ed_index='"+searchKey[1]+"';")
        cur.execute("DELETE FROM cards_owned WHERE card_name='"+searchKey[0]+"' and ed_index='"+searchKey[1]+"';")
        cur.execute("DELETE FROM card WHERE name='"+searchKey[0]+"' and ed_index='"+searchKey[1]+"';")
        con.commit()
        databasePanel.refresh()
                    
    def adduser(self):
        cur.execute("INSERT INTO users(name, pass, permission) VALUES('"+self.userName.get()+"', 'MightyMouse!', 'Basic_Access');")
        con.commit()
        self.refresh()
        
    def deluser(self, frameR):
        searchKey=self.userList.get(self.userList.curselection())
        cur.execute("select user_ID from users where name='"+searchKey[0]+"';")
        searchKey=str(cur.fetchone()[0])
        cur.execute("select deck_ID from owned_decks where user_ID="+searchKey+";")
        decks=cur.fetchall()
        for x in decks:
            cur.execute("DELETE FROM deck WHERE deck_ID="+str(x[0])+";")
        cur.execute("DELETE FROM owned_decks WHERE user_ID="+searchKey+";")
        cur.execute("DELETE FROM cards_owned WHERE user_ID="+searchKey+";")
        cur.execute("DELETE FROM users WHERE user_ID="+searchKey+";")
        con.commit()
        frameR.refresh()

    def seluser(self, rPanel):
        global uID
        uID=self.userList.get(self.userList.curselection())[1]
        rPanel.refresh()
        
    def refresh(self):
        self.userList.delete(0,END)
        cur.execute("select name,user_ID from users")
        userData=cur.fetchall()
        for x in userData:
            self.userList.insert(END, x)
            
class rightPanel:
    def __init__(self,root):
        self.frameR = Frame(root)
        self.frameR.pack(side = RIGHT)
        
        self.buttonList = LabelFrame(self.frameR, text="View Mode")
        self.buttonList.pack(fill=X)
        def colButton():
            self.cp.show()
            self.dp.hide()
            self.ap.hide()
        self.cButton = Button(self.buttonList, text="collection", command = colButton)
        self.cButton.pack(side=LEFT)
        def deckButton():
            self.cp.hide()
            self.dp.show()
            self.ap.hide()
        self.dButton = Button(self.buttonList, text="deck", command = deckButton)
        self.dButton.pack(side=LEFT)
        def admButton():
            self.cp.hide()
            self.dp.hide()
            self.ap.show()

        self.aButton = Button(self.buttonList, text="admin", command = admButton)
        self.aButton.pack(side=LEFT)
        #self.dp.deckV.pack()
        #self.cp.colV.pack()
        #self.ap.admV.pack()
        self.dp= deckPanel(self.frameR)
        self.cp= collectionPanel(self.frameR)
        self.ap= adminPanel(self.frameR)
        self.dp.hide()
        self.ap.hide()
        self.frameR.pack_forget()

        self.pwLogin=LabelFrame(root,text="login")
        self.pwLogin.pack()
        
        self.userIDin=Entry(self.pwLogin)
        self.pwIn=Entry(self.pwLogin, show='*')
        self.userIDin.pack()
        self.pwIn.pack()

        self.loginButton = Button(self.pwLogin, text="Login", command = lambda:
                                    self.login(self.userIDin.get(), self.pwIn.get()))
        self.loginButton.pack(side=LEFT)
        
    def refresh(self):
        self.dp.refresh()
        self.cp.refresh()
        self.ap.refresh()
    def login(self, usrID, pw):
        global user
        user=usrID
        connect(usrID,pw)
        self.frameR.pack()
        self.pwLogin.pack_forget()
        self.refresh()
        
from Tkinter import *
root = Tk()
user="Basic"
uID="0"
con=conn(user)
cur=con.cursor()
frameL = Frame(root)
frameL.pack(side = LEFT, fill=BOTH)

data= databasePanel(frameL)
frameR=rightPanel(root)
#various function links to external parts of the program (IE updateCard functions to the database panel)
frameR.cp.selC.config(command=lambda:frameR.cp.updateCard(data))
frameR.cp.addC.config(command=lambda:frameR.cp.addCard(data))
frameR.dp.selC.config(command=lambda:frameR.dp.updateCard(data))
frameR.dp.addC.config(command=lambda:frameR.dp.addCard(data))
frameR.ap.delC.config(command=lambda:frameR.ap.delCard(data))
frameR.ap.addC.config(command=lambda:frameR.ap.newCard(data))
frameR.ap.selU.config(command=lambda:frameR.ap.seluser(frameR))
frameR.ap.delU.config(command=lambda:frameR.ap.deluser(frameR))
mainloop()
