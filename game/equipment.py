class Equipment:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.broken = False
        self.degraded = False # Intermediate state maybe?
        
    def break_machine(self):
        self.broken = True
        
    def repair(self):
        self.broken = False
        
    def get_status(self):
        if self.broken:
            return "CASSÉ"
        return "OK"

class Fryer(Equipment):
    def __init__(self):
        super().__init__("Friteuse", "Impacte le temps de cuisson")
        self.cooking_time_multiplier = 1.0
        
    def get_multiplier(self):
        return 2.0 if self.broken else 1.0

class Spit(Equipment): # Broche
    def __init__(self):
        super().__init__("Broche", "Impacte la qualité de la viande")
        
    def get_quality_penalty(self):
        return 20 if self.broken else 0

class Menu(Equipment):
    def __init__(self):
        super().__init__("Menu", "Attire les clients")
        
    def get_client_spawn_rate_penalty(self):
        return 0.5 if self.broken else 0

class Register(Equipment): # Caisse
    def __init__(self):
        super().__init__("Caisse", "Sécurise l'argent")
        
    def get_money_loss_risk(self):
        return 0.5 if self.broken else 0.0

class Toilets(Equipment):
    def __init__(self):
        super().__init__("Toilettes", "Hygiène et inspection")
        
    def get_inspection_risk(self):
        return 0.3 if self.broken else 0.05
