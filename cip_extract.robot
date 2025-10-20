*** Settings ***
Documentation    Extraction SVG Stats CIP
Library          SeleniumLibrary
Library          OperatingSystem
Library          DateTime
Library          Collections
Resource         config.robot

Suite Setup      Set Screenshot Directory    NONE

*** Variables ***
${DOWNLOAD_DIR}             ${CURDIR}${/}downloads_cip

*** Test Cases ***
Extraire CIP Graphiques
    [Documentation]    Extraction CIP : 3 J-7→aujourd'hui, 2 jour-j, 1 J-90→aujourd'hui
    
    Create Directory    ${DOWNLOAD_DIR}
    Se connecter CRM
    Accéder Stats CIP
    
    # Extractions avec périodes
    Extraire graphiques J-7 à aujourd'hui
    Extraire graphiques jour-j
    Extraire graphique J-90 à aujourd'hui
    
    [Teardown]    Close Browser

*** Keywords ***
Accéder Menu Statistiques
    [Documentation]    Navigation vers le menu Statistiques

    Click Element    xpath=//a[@data-bs-target='#collapseStatistique']
    Sleep    0.5s
Se connecter CRM
    [Documentation]    Connexion avec configuration Chrome
    
    # Configuration Chrome
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()
    ${abs_download_dir}=    Evaluate    os.path.abspath(r'${DOWNLOAD_DIR}')    modules=os
    ${prefs}=    Create Dictionary
    ...    download.default_directory=${abs_download_dir}
    ...    download.prompt_for_download=False
    ...    credentials_enable_service=False
    ...    profile.password_manager_enabled=False
    
    Call Method    ${chrome_options}    add_experimental_option    prefs    ${prefs}
    Call Method    ${chrome_options}    add_argument    --ignore-certificate-errors
    Call Method    ${chrome_options}    add_argument    --ignore-ssl-errors
    Call Method    ${chrome_options}    add_argument    --disable-blink-features
    Call Method    ${chrome_options}    add_argument    AutomationControlled
    
    Open Browser    ${URL_WITH_AUTH}    ${BROWSER}    options=${chrome_options}
    Maximize Browser Window
    Set Selenium Timeout    10s

    # Connexion
    Wait Until Page Contains Element    id=inputEmail    10s
    Input Text    id=inputEmail    ${CRM_USERNAME}
    Input Password    id=inputPassword    ${CRM_PASSWORD}
    Click Element    xpath=//a[contains(text(),'Login')]
    Wait Until Location Contains    index.php    3s
    
    # Fermer notifications
    Run Keyword And Ignore Error    Click Element    id=close_all_notif

Accéder Stats CIP
    [Documentation]    Navigation vers Stats CIP
    
    Click Element    xpath=//a[@data-bs-target='#collapseStatistique']
    Sleep    0.05s
    Click Element    xpath=//a[@data-title='Stats CIP']
    Sleep    0.2s
    
    # Iframe detection stats_entretiens.php
    ${iframe_exists}=    Run Keyword And Return Status    
    ...    Wait Until Page Contains Element    xpath=//iframe[contains(@src,'stats_entretiens.php')]    1s
    Run Keyword If    ${iframe_exists}    Select Frame    xpath=//iframe[contains(@src,'stats_entretiens.php')]
    
    Execute Javascript    window.scrollTo(0, 0);

Extraire graphiques J-7 à aujourd'hui
    [Documentation]    Extraction 3 graphiques J-7 à aujourd'hui (button_index 4,2,0)
    
    Log    J-7 À AUJOURD'HUI (3 graphiques)
    ${today}=    Get Current Date    result_format=%Y-%m-%d
        ${j7}=    Get Current Date    increment=-7d    result_format=%Y-%m-%d
    
    # Extraction 3 graphiques button_index
    Extraire SVG CIP    4    ${j7}    ${today}    cip_j7_graph4.svg
    Extraire SVG CIP    2    ${j7}    ${today}    cip_j7_graph2.svg
    Extraire SVG CIP    0    ${j7}    ${today}    cip_j7_graph0.svg

Extraire graphiques jour-j
    [Documentation]    Extraction 2 graphiques jour-j (button_index 0,4) - CORRECTED
    
    Log    JOUR-J (2 graphiques)
    ${today}=    Get Current Date    result_format=%Y-%m-%d
    
    # Extraction 2 graphiques jour-j (indices corrigés)
    Extraire SVG CIP    0    ${today}    ${EMPTY}    cip_jourj_graph0.svg
    Extraire SVG CIP    4    ${today}    ${EMPTY}    cip_jourj_graph4.svg

Extraire graphique J-90 à aujourd'hui
    [Documentation]    Extraction 1 graphique J-90 à aujourd'hui (button_index 0)
    
    Log    J-90 À AUJOURD'HUI (1 graphique)
    ${today}=    Get Current Date    result_format=%Y-%m-%d
    ${j90}=    Get Current Date    increment=-92d    result_format=%Y-%m-%d
    
    # Extraction graphique J-90
    Extraire SVG CIP    0    ${j90}    ${today}    cip_j90_graph0.svg

Extraire SVG CIP
    [Arguments]    ${button_index}    ${date_debut}    ${date_fin}    ${filename}
    [Documentation]    Extraction SVG CIP avec debugging
    
    # DEBUG paramètres
    Log    🔍 DEBUG PARAMS - button_index: ${button_index}, date_debut: ${date_debut}, date_fin: ${date_fin}, filename: ${filename}
    
    # DEBUG valeurs AVANT
    ${values_before}=    Execute Javascript    
    ...    var buttonSelect = document.getElementById('button_index');
    ...    var dateInput1 = document.getElementById('date_1');
    ...    var dateInput2 = document.getElementById('date_2');
    ...    
    ...    return {
    ...        button_before: buttonSelect ? buttonSelect.value : 'NULL',
    ...        date1_before: dateInput1 ? dateInput1.value : 'NULL', 
    ...        date2_before: dateInput2 ? dateInput2.value : 'NULL'
    ...    };
    Log    🔍 AVANT CONFIG - ${values_before}
    
    # Interaction physique + JavaScript
    
    # DEBUG structure formulaire
    ${form_structure}=    Execute Javascript    
    ...    var result = {};
    ...    var buttonSelect = document.getElementById('button_index');
    ...    var dateInput1 = document.getElementById('date_1');
    ...    var dateInput2 = document.getElementById('date_2');
    ...    var form = document.forms[0];
    ...    
    ...    result.has_button_index = buttonSelect !== null;
    ...    result.has_date_1 = dateInput1 !== null;
    ...    result.has_date_2 = dateInput2 !== null;
    ...    result.has_form = form !== null;
    ...    
    ...    if (form) {
    ...        var inputs = form.querySelectorAll('input, select');
    ...        result.form_elements = Array.from(inputs).map(el => ({
    ...            id: el.id || 'NO_ID',
    ...            type: el.type || el.tagName.toLowerCase(),
    ...            name: el.name || 'NO_NAME'
    ...        }));
    ...    }
    ...    
    ...    return result;
    Log    🔍 STRUCTURE FORMULAIRE CIP - ${form_structure}
    
    # Click physique éléments
    Click Element    id=date_1
    Sleep    0.1s
    Run Keyword If    '${date_fin}' != ''    Click Element    id=date_2
    Run Keyword If    '${date_fin}' != ''    Sleep    0.1s
    
    # Configuration JavaScript
    Execute Javascript    
    ...    var buttonSelect = document.getElementById('button_index');
    ...    var dateInput1 = document.getElementById('date_1');
    ...    var dateInput2 = document.getElementById('date_2');
    ...    
    ...    console.log('CIP: Configuration button_index à ${button_index}');
    ...    if (buttonSelect) {
    ...        buttonSelect.focus();
    ...        buttonSelect.value = '${button_index}';
    ...        console.log('CIP: button_index value after set:', buttonSelect.value);
    ...        buttonSelect.dispatchEvent(new Event('change', { bubbles: true }));
    ...        buttonSelect.dispatchEvent(new Event('input', { bubbles: true }));
    ...    }
    ...    
    ...    console.log('CIP: Configuration date_1 à ${date_debut}');
    ...    if (dateInput1) {
    ...        dateInput1.focus();
    ...        dateInput1.value = '${date_debut}';
    ...        console.log('CIP: date_1 value after set:', dateInput1.value);
    ...        dateInput1.dispatchEvent(new Event('change', { bubbles: true }));
    ...        dateInput1.dispatchEvent(new Event('input', { bubbles: true }));
    ...        dateInput1.checkValidity();
    ...    }
    ...    
    ...    if (dateInput2 && '${date_fin}' !== '') {
    ...        console.log('CIP: Configuration date_2 à ${date_fin}');
    ...        dateInput2.focus();
    ...        dateInput2.value = '${date_fin}';
    ...        console.log('CIP: date_2 value after set:', dateInput2.value);
    ...        dateInput2.dispatchEvent(new Event('change', { bubbles: true }));
    ...        dateInput2.dispatchEvent(new Event('input', { bubbles: true }));
    ...        dateInput2.checkValidity();
    ...    }
    
    Sleep    0.3s
    
    # DEBUG valeurs APRÈS
    ${values_after}=    Execute Javascript    
    ...    var buttonSelect = document.getElementById('button_index');
    ...    var dateInput1 = document.getElementById('date_1');
    ...    var dateInput2 = document.getElementById('date_2');
    ...    
    ...    return {
    ...        button_after: buttonSelect ? buttonSelect.value : 'NULL',
    ...        date1_after: dateInput1 ? dateInput1.value : 'NULL',
    ...        date2_after: dateInput2 ? dateInput2.value : 'NULL'
    ...    };
    Log    🔍 APRÈS CONFIG - ${values_after}
    
    # Recherche et extraction
    Click Element    id=envoyer
    Sleep    1.2s
    
    # Nettoyage menus
    Execute Javascript    
    ...    document.querySelectorAll('.highcharts-contextmenu, .highcharts-menu').forEach(function(menu) {
    ...        if (menu && menu.style) {
    ...            menu.style.display = 'none';
    ...            menu.style.visibility = 'hidden';
    ...        }
    ...    });
    ...    document.body.click();
    
    # Extraction SVG - CORRIGER : utiliser le bon index selon button_index
    @{svg_elements}=    Get WebElements    xpath=//*[name()='svg' and contains(@class,'highcharts-root')]
    ${svg_count}=    Get Length    ${svg_elements}
    
    Log    🔍 EXTRACTION SVG - button_index: ${button_index}, SVG trouvés: ${svg_count}
    
    IF    ${svg_count} > 0
        # Extraire TOUS les SVG et identifier le bon selon button_index ou position
        ${exports_reussis}=    Set Variable    0
        ${index}=    Set Variable    0
        
        # Pour déboguer, extraire tous les SVG avec des noms différents
        FOR    ${svg_element}    IN    @{svg_elements}
            ${svg_content}=    Execute Javascript
            ...    var svg = arguments[0];
            ...    return new XMLSerializer().serializeToString(svg);
            ...    ARGUMENTS    ${svg_element}
            
            # Créer un nom de fichier avec l'index pour le debug
            ${debug_filename}=    Set Variable    debug_${filename}_idx${index}.svg
            Create File    ${DOWNLOAD_DIR}/${debug_filename}    ${svg_content}
            Log    🐛 DEBUG SVG ${index} sauvé: ${debug_filename}
            
            # Utiliser le SVG correspondant au button_index (ou le premier si problème)
            IF    ${index} == ${button_index} or ${svg_count} == 1
                Create File    ${DOWNLOAD_DIR}/${filename}    ${svg_content}
                Log    ✅ SVG CIP sauvegardé: ${filename} (button_index ${button_index}, SVG index ${index})
                ${exports_reussis}=    Set Variable    1
            END
            
            ${index}=    Evaluate    ${index} + 1
        END
        
        # Si aucun SVG correspondant, utiliser le premier
        IF    ${exports_reussis} == 0
            ${svg_content}=    Execute Javascript
            ...    var svg = arguments[0];
            ...    return new XMLSerializer().serializeToString(svg);
            ...    ARGUMENTS    ${svg_elements}[0]
            
            Create File    ${DOWNLOAD_DIR}/${filename}    ${svg_content}
            Log    ⚠️ SVG CIP sauvegardé (fallback): ${filename} (button_index ${button_index})
        END
    ELSE
        Log    ❌ Aucun SVG trouvé pour button_index ${button_index}
        
        # Autres sélecteurs SVG CIP
        @{svg_alt}=    Get WebElements    xpath=//svg
        ${svg_alt_count}=    Get Length    ${svg_alt}
        
        IF    ${svg_alt_count} > 0
            ${svg_alt_content}=    Execute Javascript
            ...    var svg = arguments[0];
            ...    return new XMLSerializer().serializeToString(svg);
            ...    ARGUMENTS    ${svg_alt}[0]
            
            Create File    ${DOWNLOAD_DIR}/${filename}    ${svg_alt_content}
            Log    ✅ SVG CIP alternatif sauvegardé: ${filename} (button_index ${button_index})
        END
    END