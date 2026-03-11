import undetected_chromedriver as uc
import time


def criar_driver():

    print("Inicializando o Chrome em modo Stealth (Undetected)...")

    options = uc.ChromeOptions()


    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = uc.Chrome(options=options)

    return driver


if __name__ == "__main__":
    driver = criar_driver()
    driver.get("https://fbref.com/pt/comps/24/horario/Serie-A-Resultados-e-Calendarios")
    time.sleep(5)
    print("Título da página: ", driver.title)
    driver.quit()