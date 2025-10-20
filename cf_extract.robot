*** Settings ***
Documentation    Extraction SVG Stats CF
Library          SeleniumLibrary
Library          OperatingSystem
Library          DateTime
Library          Collections
Library          String
Resource         config.robot

Suite Setup      Set Screenshot Directory    NONE

*** Variables ***
${DOWNLOAD_DIR}             ${CURDIR}${/}downloads_cf

*** Test Cases ***
Extraire CF Graphiques
    [Documentation]    Extraction 5 graphiques CF périodes spécifiques
    
    Create Directory    ${DOWNLOAD_DIR}
    Se connecter CRM
    Accéder Stats CF
    
    # Extractions
    Extraire graphiques jour-j
    Extraire graphiques semaine précédente  
    Extraire graphique J-90
    
    [Teardown]    Close Browser

*** Keywords ***
Se connecter CRM
    [Documentation]    Connexion CRM avec Chrome
    
    # Chrome config
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

Accéder Stats CF
    [Documentation]    Navigation vers Stats CF

    Click Element    xpath=//a[@data-bs-target='#collapseStatistique']
    Sleep    0.5s
    Wait Until Element Is Visible    xpath=//a[@data-title='Stats CF']    3s
    Click Element    xpath=//a[@data-title='Stats CF']
    Sleep    0.2s
    
    # Iframe detection
    ${iframe_exists}=    Run Keyword And Return Status    
    ...    Wait Until Page Contains Element    xpath=//iframe[contains(@src,'stats_cf.php')]    1s
    Run Keyword If    ${iframe_exists}    Select Frame    xpath=//iframe[contains(@src,'stats_cf.php')]
    
    Execute Javascript    window.scrollTo(0, 0);

Extraire graphiques jour-j
    [Documentation]    Extraction 2 graphiques jour-j en une seule recherche
    
    Log    JOUR-J (2 graphiques en une fois)
    ${today}=    Get Current Date    result_format=%Y-%m-%d
    
    # Extraction optimisée - une seule recherche pour les 2 graphiques jour-j
    Extraire plusieurs SVG CF    ${today}    ${EMPTY}    jourj_graph2.svg,jourj_graph4.svg    2,4

Extraire graphiques semaine précédente
    [Documentation]    Extraction 2 graphiques semaine précédente en une seule recherche
    
    Log    SEMAINE PRÉCÉDENTE (2 graphiques en une fois)
    ${j7}=    Get Current Date    increment=-7d    result_format=%Y-%m-%d
    
    # Extraction optimisée - une seule recherche pour les 2 graphiques semaine précédente
    Extraire plusieurs SVG CF    ${j7}    ${EMPTY}    semaine_precedente_graph3.svg,semaine_precedente_graph4.svg    3,4

Extraire graphique J-90
    [Documentation]    Extraction 1 graphique J-90 groupé par semaine avec téléchargement menu
    
    Log    J-90 GROUPÉ SEMAINE (1 graphique)
    ${today}=    Get Current Date    result_format=%Y-%m-%d
    ${j90}=    Get Current Date    increment=-92d    result_format=%Y-%m-%d
    
    # Configuration J-90 et téléchargement en une seule étape
    Configurer et télécharger J-90    ${j90}    ${today}    j90_semaine_graph4.svg

Extraire SVG CF
    [Arguments]    ${button_index}    ${date_debut}    ${date_fin}    ${filename}
    [Documentation]    Extraction SVG CF avec debugging (même méthode que CIP)
    
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
    Log    🔍 STRUCTURE FORMULAIRE CF - ${form_structure}
    
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
    ...    console.log('CF: Configuration button_index à ${button_index}');
    ...    if (buttonSelect) {
    ...        buttonSelect.focus();
    ...        buttonSelect.value = '${button_index}';
    ...        console.log('CF: button_index value after set:', buttonSelect.value);
    ...        buttonSelect.dispatchEvent(new Event('change', { bubbles: true }));
    ...        buttonSelect.dispatchEvent(new Event('input', { bubbles: true }));
    ...    }
    ...    
    ...    console.log('CF: Configuration date_1 à ${date_debut}');
    ...    if (dateInput1) {
    ...        dateInput1.focus();
    ...        dateInput1.value = '${date_debut}';
    ...        console.log('CF: date_1 value after set:', dateInput1.value);
    ...        dateInput1.dispatchEvent(new Event('change', { bubbles: true }));
    ...        dateInput1.dispatchEvent(new Event('input', { bubbles: true }));
    ...        dateInput1.checkValidity();
    ...    }
    ...    
    ...    if (dateInput2 && '${date_fin}' !== '') {
    ...        console.log('CF: Configuration date_2 à ${date_fin}');
    ...        dateInput2.focus();
    ...        dateInput2.value = '${date_fin}';
    ...        console.log('CF: date_2 value after set:', dateInput2.value);
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
    Sleep    1.8s
    
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
                Log    ✅ SVG CF sauvegardé: ${filename} (button_index ${button_index}, SVG index ${index})
                ${exports_reussis}=    Set Variable    1
            END
            
            ${index}=    Evaluate    ${index} + 1
        END
        
        IF    ${exports_reussis} == 0
            Log    ⚠️ Aucun SVG CF correspondant au button_index ${button_index}, ${svg_count} SVG(s) trouvé(s)
        END
    ELSE
        Log    ❌ Aucun SVG CF trouvé pour button_index ${button_index}
    END

Configurer J-90
    [Arguments]    ${date_debut}    ${date_fin}
    [Documentation]    Configuration J-90 groupement semaine
    
    # Configuration JavaScript
    Execute Javascript    
    ...    var buttonSelect = document.getElementById('button_index');
    ...    var groupeSelect = document.getElementById('groupe');
    ...    var dateInput1 = document.getElementById('date_1');
    ...    var dateInput2 = document.getElementById('date_2');
    ...    
    ...    // Configuration button_index 4
    ...    if (buttonSelect) {
    ...        buttonSelect.value = '4';
    ...        buttonSelect.dispatchEvent(new Event('change', { bubbles: true }));
    ...    }
    ...    
    ...    // Configuration groupement par semaine
    ...    if (groupeSelect) {
    ...        groupeSelect.value = 'semaine';
    ...        groupeSelect.dispatchEvent(new Event('change', { bubbles: true }));
    ...    }
    ...    
    ...    // Configuration période 3 mois
    ...    if (dateInput1) {
    ...        dateInput1.value = '${date_debut}';
    ...        dateInput1.dispatchEvent(new Event('change', { bubbles: true }));
    ...    }
    ...    if (dateInput2) {
    ...        dateInput2.value = '${date_fin}';
    ...        dateInput2.dispatchEvent(new Event('change', { bubbles: true }));
    ...    }
    
    Sleep    0.5s

Extraire SVG direct
    [Arguments]    ${filename}
    [Documentation]    Extraction SVG sans reconfiguration
    
    Click Element    id=envoyer
    Sleep    2.5s
    
    # Nettoyage des menus
    Execute Javascript    
    ...    document.querySelectorAll('.highcharts-contextmenu, .highcharts-menu').forEach(function(menu) {
    ...        if (menu && menu.style) {
    ...            menu.style.display = 'none';
    ...            menu.style.visibility = 'hidden';
    ...        }
    ...    });
    ...    document.body.click();
    
    # Extraction SVG
    @{svg_elements}=    Get WebElements    xpath=//*[name()='svg' and contains(@class,'highcharts-root')]
    ${svg_count}=    Get Length    ${svg_elements}
    
    IF    ${svg_count} > 0
        # Extraire tous les SVG via JavaScript pour éviter les références obsolètes
        ${all_svg_contents}=    Execute Javascript    
        ...    var svgs = document.querySelectorAll('svg.highcharts-root');
        ...    var contents = [];
        ...    for (var i = 0; i < svgs.length; i++) {
        ...        contents.push(new XMLSerializer().serializeToString(svgs[i]));
        ...    }
        ...    return contents;
        
        ${index}=    Set Variable    0
        ${dernier_svg_content}=    Set Variable    ${EMPTY}
        
        # Pour déboguer, sauvegarder tous les SVG
        FOR    ${svg_content}    IN    @{all_svg_contents}
            # Créer un fichier de débogage pour chaque SVG trouvé
            ${debug_filename}=    Set Variable    debug_cf_j90_svg_${index}.svg
            Create File    ${DOWNLOAD_DIR}/${debug_filename}    ${svg_content}
            Log    📊 SVG CF J-90 debug sauvegardé: ${debug_filename}
            
            # Garder le contenu du dernier SVG (habituellement le graphique principal)
            ${dernier_svg_content}=    Set Variable    ${svg_content}
            ${index}=    Evaluate    ${index} + 1
        END
        
        # Sauvegarder le fichier final avec le dernier SVG
        Create File    ${DOWNLOAD_DIR}/${filename}    ${dernier_svg_content}
        Log    ✅ SVG CF J-90 sauvegardé: ${filename} (${svg_count} SVG(s) trouvé(s), dernier utilisé)
    ELSE
        Log    ❌ Aucun SVG CF J-90 trouvé

Télécharger SVG via menu
    [Arguments]    ${filename}
    [Documentation]    Téléchargement SVG via le menu Highcharts (séquence complète)
    
    # 1. Lancer la recherche
    Click Element    id=envoyer
    Sleep    2.0s
    
    # 2. Cliquer sur le menu Highcharts (les 3 lignes)
    ${menu_button}=    Get WebElement    xpath=//path[@class='highcharts-button-symbol']
    Click Element    ${menu_button}
    Sleep    0.5s
    
    # 3. Cliquer sur "Download SVG vector image"
    ${svg_download}=    Get WebElement    xpath=//li[contains(text(),'Download SVG vector image')]
    Click Element    ${svg_download}
    Sleep    1.0s
    
    Log    ✅ Téléchargement SVG via menu: ${filename}

Configurer et télécharger J-90
    [Arguments]    ${date_debut}    ${date_fin}    ${filename}
    [Documentation]    Configuration complète J-90 + téléchargement via menu en une fois
    
    # Configuration complète avec interactions physiques
    Click Element    id=date_1
    Sleep    0.1s
    Click Element    id=date_2
    Sleep    0.1s
    
    # Configuration JavaScript (comme dans Extraire SVG CF)
    Execute Javascript    
    ...    var buttonSelect = document.getElementById('button_index');
    ...    var groupeSelect = document.getElementById('groupe');
    ...    var dateInput1 = document.getElementById('date_1');
    ...    var dateInput2 = document.getElementById('date_2');
    ...    
    ...    console.log('J-90: Configuration button_index à 4');
    ...    if (buttonSelect) {
    ...        buttonSelect.focus();
    ...        buttonSelect.value = '4';
    ...        buttonSelect.dispatchEvent(new Event('change', { bubbles: true }));
    ...        buttonSelect.dispatchEvent(new Event('input', { bubbles: true }));
    ...    }
    ...    
    ...    console.log('J-90: Configuration groupement semaine');
    ...    if (groupeSelect) {
    ...        groupeSelect.focus();
    ...        groupeSelect.value = 'semaine';
    ...        groupeSelect.dispatchEvent(new Event('change', { bubbles: true }));
    ...        groupeSelect.dispatchEvent(new Event('input', { bubbles: true }));
    ...    }
    ...    
    ...    console.log('J-90: Configuration date_1 à ${date_debut}');
    ...    if (dateInput1) {
    ...        dateInput1.focus();
    ...        dateInput1.value = '${date_debut}';
    ...        dateInput1.dispatchEvent(new Event('change', { bubbles: true }));
    ...        dateInput1.dispatchEvent(new Event('input', { bubbles: true }));
    ...        dateInput1.checkValidity();
    ...    }
    ...    
    ...    console.log('J-90: Configuration date_2 à ${date_fin}');
    ...    if (dateInput2) {
    ...        dateInput2.focus();
    ...        dateInput2.value = '${date_fin}';
    ...        dateInput2.dispatchEvent(new Event('change', { bubbles: true }));
    ...        dateInput2.dispatchEvent(new Event('input', { bubbles: true }));
    ...        dateInput2.checkValidity();
    ...    }
    
    Sleep    0.5s
    
    # Lancer la recherche
    Click Element    id=envoyer
    Sleep    2.0s
    
    # Téléchargement via menu Highcharts - sélecteurs plus robustes
    ${menu_clicked}=    Run Keyword And Return Status
    ...    Run Keywords
    ...    Wait Until Element Is Visible    xpath=//button[contains(@class,'highcharts-button')]    3s    AND
    ...    Click Element    xpath=//button[contains(@class,'highcharts-button')]    AND
    ...    Sleep    0.5s
    
    IF    ${menu_clicked}
        ${download_clicked}=    Run Keyword And Return Status
        ...    Run Keywords
        ...    Wait Until Element Is Visible    xpath=//li[contains(text(),'SVG') or contains(text(),'Download')]    2s    AND
        ...    Click Element    xpath=//li[contains(text(),'SVG') or contains(text(),'Download')]    AND
        ...    Sleep    1.0s
        
        IF    ${download_clicked}
            Log    ✅ Téléchargement via menu réussi
        ELSE
            Log    ❌ Menu de téléchargement non trouvé - utilisation extraction DOM
            # Fallback vers extraction DOM
            @{svg_elements}=    Get WebElements    xpath=//*[name()='svg' and contains(@class,'highcharts-root')]
            ${svg_element_count}=    Get Length    ${svg_elements}
            IF    ${svg_element_count} > 0
                ${svg_content}=    Execute Javascript
                ...    var svgs = document.querySelectorAll('svg.highcharts-root');
                ...    return svgs.length > 0 ? new XMLSerializer().serializeToString(svgs[svgs.length-1]) : '';
                Create File    ${DOWNLOAD_DIR}/${filename}    ${svg_content}
                Log    ✅ J-90 extrait via DOM (fallback)
            END
        END
    ELSE
        Log    ❌ Bouton menu Highcharts non trouvé - extraction DOM directe
        # Extraction DOM directe
        @{svg_elements}=    Get WebElements    xpath=//*[name()='svg' and contains(@class,'highcharts-root')]
        ${svg_element_count_direct}=    Get Length    ${svg_elements}
        IF    ${svg_element_count_direct} > 0
            ${svg_content}=    Execute Javascript
            ...    var svgs = document.querySelectorAll('svg.highcharts-root');
            ...    return svgs.length > 0 ? new XMLSerializer().serializeToString(svgs[svgs.length-1]) : '';
            Create File    ${DOWNLOAD_DIR}/${filename}    ${svg_content}
            Log    ✅ J-90 extrait via DOM (direct)
        END
    END
    
    Log    ✅ J-90 configuré et téléchargé: ${filename} (${date_debut} au ${date_fin})

Extraire plusieurs SVG CF
    [Arguments]    ${date_debut}    ${date_fin}    ${filenames}    ${button_indices}
    [Documentation]    Extraction multiple SVG CF en une seule recherche
    
    # Séparer les paramètres multiples
    @{filename_list}=    Split String    ${filenames}    ,
    @{index_list}=    Split String    ${button_indices}    ,
    
    Log    🔍 Extraction multiple: ${filename_list} avec button_indices ${index_list}
    
    # Configuration des dates (une seule fois)
    Click Element    id=date_1
    Sleep    0.1s
    Run Keyword If    '${date_fin}' != ''    Click Element    id=date_2
    Run Keyword If    '${date_fin}' != ''    Sleep    0.1s
    
    Execute Javascript    
    ...    var dateInput1 = document.getElementById('date_1');
    ...    var dateInput2 = document.getElementById('date_2');
    ...    
    ...    if (dateInput1) {
    ...        dateInput1.focus();
    ...        dateInput1.value = '${date_debut}';
    ...        dateInput1.dispatchEvent(new Event('change', { bubbles: true }));
    ...        dateInput1.dispatchEvent(new Event('input', { bubbles: true }));
    ...    }
    ...    
    ...    if (dateInput2 && '${date_fin}' !== '') {
    ...        dateInput2.focus();
    ...        dateInput2.value = '${date_fin}';
    ...        dateInput2.dispatchEvent(new Event('change', { bubbles: true }));
    ...        dateInput2.dispatchEvent(new Event('input', { bubbles: true }));
    ...    }
    
    Sleep    0.3s
    
    # Une seule recherche pour tous les graphiques
    Click Element    id=envoyer
    Sleep    1.8s
    
    # Nettoyage menus
    Execute Javascript    
    ...    document.querySelectorAll('.highcharts-contextmenu, .highcharts-menu').forEach(function(menu) {
    ...        if (menu && menu.style) {
    ...            menu.style.display = 'none';
    ...            menu.style.visibility = 'hidden';
    ...        }
    ...    });
    
    # Extraction de tous les SVG
    @{svg_elements}=    Get WebElements    xpath=//*[name()='svg' and contains(@class,'highcharts-root')]
    ${svg_count}=    Get Length    ${svg_elements}
    
    ${filename_count}=    Get Length    ${filename_list}
    Log    🔍 EXTRACTION MULTIPLE - SVG trouvés: ${svg_count}, fichiers demandés: ${filename_count}
    
    IF    ${svg_count} > 0
        # Extraire tous les SVG avec debugging
        ${svg_index}=    Set Variable    0
        FOR    ${svg_element}    IN    @{svg_elements}
            ${svg_content}=    Execute Javascript
            ...    var svg = arguments[0];
            ...    return new XMLSerializer().serializeToString(svg);
            ...    ARGUMENTS    ${svg_element}
            
            # Debug: sauvegarder tous les SVG
            ${debug_filename}=    Set Variable    debug_multi_svg_${svg_index}.svg
            Create File    ${DOWNLOAD_DIR}/${debug_filename}    ${svg_content}
            
            ${svg_index}=    Evaluate    ${svg_index} + 1
        END
        
        # Associer chaque filename à son button_index correspondant
        ${file_index}=    Set Variable    0
        FOR    ${filename}    IN    @{filename_list}
            ${button_index}=    Get From List    ${index_list}    ${file_index}
            ${button_index}=    Convert To Integer    ${button_index}
            
            # Chercher le SVG correspondant au button_index
            ${found_svg}=    Set Variable    ${False}
            ${check_index}=    Set Variable    0
            FOR    ${svg_element}    IN    @{svg_elements}
                IF    ${check_index} == ${button_index} or ${svg_count} == 1
                    ${svg_content}=    Execute Javascript
                    ...    var svg = arguments[0];
                    ...    return new XMLSerializer().serializeToString(svg);
                    ...    ARGUMENTS    ${svg_element}
                    
                    Create File    ${DOWNLOAD_DIR}/${filename}    ${svg_content}
                    Log    ✅ SVG CF multiple sauvé: ${filename} (button_index ${button_index})
                    ${found_svg}=    Set Variable    ${True}
                    BREAK
                END
                ${check_index}=    Evaluate    ${check_index} + 1
            END
            
            IF    not ${found_svg}
                Log    ⚠️ SVG non trouvé pour ${filename} (button_index ${button_index})
            END
            
            ${file_index}=    Evaluate    ${file_index} + 1
        END
    ELSE
        Log    ❌ Aucun SVG trouvé pour extraction multiple
    END