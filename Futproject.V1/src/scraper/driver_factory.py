import undetected_chromedriver as uc


def criar_driver():
    print("Inicializando o Chrome em modo Headless...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options)
    return driver


if __name__ == "__main__":
    import time
    driver = criar_driver()
    driver.get("https://fbref.com/pt/comps/24/horario/Serie-A-Resultados-e-Calendarios")
    time.sleep(5)
    print("Título da página: ", driver.title)
    driver.quit()