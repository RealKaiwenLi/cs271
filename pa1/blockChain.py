import hashlib

class Block:
    def __init__(self,S,R,amt, prevHash):
        self.S = S
        self.R = R
        self.amt = amt
        self.prevHash = prevHash
        self.next = None
    
class Blockchain:
    def __init__(self):
        self.genesis = Block("Genesis","Genesis",0,None)
        
    def getTheHash(self, S,R,amt,prev):
        val = str(S) + str(R) + str(amt)
        val = val.encode()
        prev = str(prev).encode()
        # Check this operation --> is it concat or bitwise "OR" operation 
        HashInp = val + prev
        prevHash = hashlib.sha256(HashInp)
        return prevHash.hexdigest()


    def insert(self, sender, rec, amt):
        
        if self.validate(sender,amt):
            temp = self.genesis
            while temp.next != None:
                    temp = temp.next
            Hash = self.getTheHash(temp.S,temp.R,temp.amt,temp.prevHash)
            newBlock = Block(sender,rec,amt,Hash)
            temp.next = newBlock
            return "SUCCESS"
        else:
            return "INCORRECT"
        
    def Show(self):
        print("Current blockchain:")
        temp = self.genesis.next
        while temp:
                print("Sender: {} Reciever: {} Amount: {} PreviousHash: {}".format(temp.S,temp.R,temp.amt, temp.prevHash))
                temp = temp.next
                
                
    def validate(self ,sender, amount):
        currentBalance = self.balance(sender)
        if amount <= currentBalance:
            return True
        else:
            return False
        
    def balance(self,client):
        temp = self.genesis.next
        Balance = 10
        while temp:
            if temp.S == client:
                Balance -= temp.amt
            elif temp.R == client:
                Balance += temp.amt
            temp = temp.next
        return Balance
                