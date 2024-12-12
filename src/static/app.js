const fileBtn = document.getElementById('fileBtn');
const removeBtn = document.getElementById('removeBtn');
const jsonTree = document.getElementById('jsonTree');
const sendBtn = document.getElementById('sendBtn');
const saveBtn = document.getElementById('saveBtn');
const closeBtn = document.getElementById('closeBtn');
const contain = document.getElementById('container');

let scrollPositionContainer = localStorage.getItem('scrollPositionContainer');
let dimensionValues = [];
let typeValues = [];
let jsonData;
let openedNodes = [];

try {
    jsonData = JSON.parse(localStorage.getItem('jsonData'));
    openedNodes = JSON.parse(localStorage.getItem('openedNodes'));
    dimensionValues = JSON.parse(localStorage.getItem('dimensionValues'))['data'];
    typeValues = JSON.parse(localStorage.getItem('typeValues'))['data'];
} catch { }

contain.addEventListener('scroll', function () {
    localStorage.setItem('scrollPositionContainer', contain.scrollTop);
});

function updateButtonsState() { //видимость кнопок в заголовке
    const listItems = jsonTree.querySelectorAll('li');
    const hasItems = listItems.length > 0;
    removeBtn.disabled = !hasItems;
    sendBtn.disabled = !hasItems;
    closeBtn.disabled = !hasItems;
}

document.addEventListener('DOMContentLoaded', function () { //При обновлении
    if (jsonData !== undefined && jsonData !== null) {
        renderJsonTree(jsonData, jsonTree, openedNodes);
    }
    removeBtn.style.display = 'block';
    updateButtonsState();
    contain.scrollTop = parseInt(scrollPositionContainer, 10);
});

fileBtn.addEventListener('click', handleFileUpload);
removeBtn.addEventListener('click', handleRemoveFile);
closeBtn.addEventListener('click', handleCloseFile);
sendBtn.addEventListener('click', handleSendFile);
saveBtn.addEventListener('click', redirectToBack);

function handleCloseFile() { //сворачивание дерева
    openedNodes = [];
    localStorage.setItem('openedNodes', JSON.stringify(openedNodes));
    let nestedLists = Array.from(jsonTree.querySelectorAll('li')).filter(li => !li.classList.contains('property') && li.querySelector('.toggle').textContent === '-');
    nestedLists.forEach(nestedList => {
        nestedList.querySelector('ul').classList.add('hidden');        
        nestedList.querySelector('.toggle').textContent = '+';
    });
    updateButtonsState();
}

function handleFileUpload(event) { //Загрузка новой схемы
    jsonTree.innerHTML = '';
    localStorage.removeItem('jsonData');
    localStorage.removeItem('openedNodes');

    jsonData = vvkScheme;
    dimensionValues = [];
    typeValues = [];
    openedNodes = [];

    Object.keys(jsonData['scheme']['metrics']).forEach(metric => {
        if (!dimensionValues.includes(jsonData['scheme']['metrics'][metric]['dimension'])) {
            dimensionValues.push(jsonData['scheme']['metrics'][metric]['dimension']);
        }
        if (!typeValues.includes(jsonData['scheme']['metrics'][metric]['type'])) {
            typeValues.push(jsonData['scheme']['metrics'][metric]['type']);
        }
    });

    const item_info_list_map = {};
    if (jsonData['scheme']['item_info_list']) {
        jsonData['scheme']['item_info_list'].forEach(item => {
            item_info_list_map[item.full_path] = item;
        });
    }

    jsonData['scheme']['item_id_list'].forEach(item => {
        if (item_info_list_map[item.full_path]) {
            item['info'] = item_info_list_map[item.full_path];
        }
    });


    localStorage.setItem('dimensionValues', JSON.stringify({ "data": dimensionValues }));
    localStorage.setItem('typeValues', JSON.stringify({ "data": typeValues }));
    localStorage.setItem('jsonData', JSON.stringify(jsonData));
    localStorage.setItem('openedNodes', JSON.stringify(openedNodes));
    renderJsonTree(jsonData, jsonTree);
    updateButtonsState();
}

function handleRemoveFile() {//Удаление схемы
    if (confirm('Удалить схему из редактора?')) {
        jsonTree.innerHTML = '';
        updateButtonsState();
        localStorage.removeItem('jsonData');
        localStorage.removeItem('openedNodes');
    }
}

function handleSendFile() {//Отправляю схему на АТ
    if (confirm('Отправить схему?')) {
        const url = 'http://localhost:' + my_port.toString() +'/editor/save';   // адрес отправления схемы
        const sr = parseInt(jsonData['scheme_revision']) + 1
        jsonData['scheme_revision'] = sr;
        localStorage.setItem('jsonData', JSON.stringify(jsonData));

        let liList = jsonTree.querySelectorAll('li');
        liList.forEach(li => {
            const liKey = li.querySelector('.key');
            if (liKey?.textContent === 'scheme_revision') {
                li.querySelector('input.input-field').value = sr;
            }
        });

        let scheme = jsonData;
        scheme['scheme']['item_id_list'].forEach(item => {
            if (item['info']) { delete item['info']; }
        });       
        
        const requestTime = new Date().toLocaleTimeString();
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(scheme)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response);
                }
                const responseTime = new Date().toLocaleTimeString();
                return response.json().then(data => ({
                    data: data,
                    requestTime: requestTime,
                    responseTime: responseTime
                }));
            })
            .then(({ data, requestTime, responseTime }) => {
                alert(`Время отправки запроса: ${requestTime}\nВремя получения ответа: ${responseTime}\nОтвет: ${JSON.stringify(data)}\nНомер ревизии схемы: ${sr}`);
            })
            .catch(error => {
                alert('Ошибка: ' + error.message);
            });
    }
}
// названия полей, которые нужно редактировать
const editableFields = ['name', 'comment', 'err_thr_max', 'err_thr_min', 'description', 'sn', 'number'];
function renderJsonTree(data, parentElement, openedNodes = [], parent = '', chapter = '', keyWey = '') { //рекурсивная отрисовка дерева
    let parentName = '';
    if (parent !== '') { parentName = parent.querySelector('.key').textContent; }
    keyWey += (keyWey === '') ? parentName : '.' + parentName;    

    Object.keys(data).forEach(key => {
        if ((['includes', 'metric_info_list'].includes(key) && data[key].length === 0) || (['column_name', 'table_name'].includes(key))) { return; }
        if (['item_info_list', 'metrics', 'metric_info_list', 'item_id_list', 'templates'].includes(key)) { chapter = key; }
        const listItem = document.createElement('li');
        const toggleButton = document.createElement('span');        
        
        //установил имя
        const NameValue = document.createElement('span');
        if (['metrics', 'templates'].includes(parentName)) {
            NameValue.textContent = data[key]['name'];
        } else if (['item_id_list', 'item_info_list'].includes(parentName)) {
            NameValue.textContent = data[key]['full_path'];
        } else if (['metric_info_list'].includes(parentName)) {
            NameValue.textContent = data[key]['item_id'];
        } else if (parentName === 'includes') {
            NameValue.textContent = data[key]['template_id'];
        } else {
            NameValue.textContent = key;
        }
        NameValue.className = 'key';

        const fullKeyWey = (keyWey === '') ? NameValue.textContent : keyWey + '.' + NameValue.textContent;
        const isOpen = openedNodes.includes(fullKeyWey);

        toggleButton.textContent = typeof data[key] === 'object' && data[key] !== null ? (isOpen ? '-' : '+') : '';
        toggleButton.className = 'toggle';

        const buttonGroup = document.createElement('span');
        buttonGroup.className = 'button-group';

        //Кнопки + info
        if (parentName === 'item_id_list' && !data[key]['info']) {
            plusButtonInfo(buttonGroup, data[key]['full_path'], key);           
        }

        //Кнопки для добавления полей + [имя_атрибута]
        if (key === 'info' || parentName === 'item_info_list') {
            ['comment', 'sn', 'name', 'number'].forEach(el => {
                plusButtonField(el, buttonGroup, data[key]);
            });
        }

        if (!['full_path', 'item_info_list'].includes(key)) {
            if (parentName === 'info' || chapter === 'item_info_list' || key === 'info') {
                delete_button(buttonGroup, data, key, parentName);
            }
        }

        const valueElement = document.createElement('span');
        if (typeof data[key] === 'object' && data[key] !== null) {
            valueElement.className = 'value';
            const nestedList = document.createElement('ul');
            nestedList.className = 'json-tree' + (isOpen ? '' : ' hidden');            

            listItem.appendChild(toggleButton);
            listItem.appendChild(NameValue);
            listItem.appendChild(buttonGroup);
            listItem.appendChild(nestedList);
            
            toggleButton.addEventListener('click', function (event) {
                nestedList.classList.toggle('hidden');
                toggleButton.textContent = nestedList.classList.contains('hidden') ? '+' : '-';
                updateOpenedNodes(fullKeyWey, !nestedList.classList.contains('hidden'));
                event.stopPropagation();
            });            
            renderJsonTree(data[key], nestedList, openedNodes, listItem, chapter, keyWey);

        } else {
            listItem.classList.add('property');
            if (['err_thr_max', 'err_thr_min'].includes(key)) {   //дробные числа
                const inputField = document.createElement('input');
                inputField.placeholder = 'Введите значение'; 
                inputField.type = 'number';
                inputField.value = data[key].toString().replace(',', '.');
                inputField.className = 'input-field';
                inputField.step = 'any';
                inputField.readOnly = (!editableFields.includes(key));
                inputField.addEventListener('change', function () {
                    const value = parseFloat(inputField.value);
                    if (!isNaN(value)) {
                        changeField(chapter, data['metric_id'], 'metric_id', value, key);
                        data[key] = value;
                        localStorage.setItem('jsonData', JSON.stringify(jsonData));
                    }
                });
                valueElement.appendChild(inputField);
            } else if (['query_interval', 'number'].includes(key)) {  //целые
                const inputField = document.createElement('input');
                inputField.placeholder = 'Введите значение'; 
                inputField.type = 'number';
                inputField.value = data[key];
                inputField.className = 'input-field';
                inputField.step = '1';
                inputField.readOnly = (!editableFields.includes(key));
                inputField.addEventListener('change', function () {
                    const value = parseInt(inputField.value);
                    if (!isNaN(value)) {
                        data[key] = value;
                        if (parentName === 'info') { 
                            jsonData['scheme']['item_id_list'].forEach(item => {
                                if (item['full_path'] === data['full_path']) {
                                    item['info'][key] = value;
                                }
                            });
                            updateLi(data, key, value);
                        } else if (chapter === 'item_info_list') {
                            changeField(chapter, data['full_path'], 'full_path', value, key);
                            updateInfoList(data, key, value);
                        }
                        localStorage.setItem('jsonData', JSON.stringify(jsonData));
                    }
                });
                valueElement.appendChild(inputField);
                //} else if (['is_config', 'dimension', 'type'].includes(key)) {   //выпадающие списки
            //     const inputField = document.createElement('input');
            //     inputField.placeholder = 'Выберите значение';
            //     inputField.className = 'input-field';
            //     inputField.readOnly = (!editableFields.includes(key));
            //     // if (key === 'is_config') {
            //     //     addOptions(inputField, ['true', 'false']);
            //     // } else if (key === 'dimension') {
            //     //     addOptions(inputField, dimensionValues);
            //     // } else if (key === 'type') {
            //     //     addOptions(inputField, typeValues);
            //     // }
            //     inputField.value = data[key].toString();
            //     // inputField.addEventListener('change', function () {
            //     //     if (key === 'is_config') {
            //     //         data[key] = selectField.value === 'true';
            //     //         localStorage.setItem('jsonData', JSON.stringify(jsonData));
            //     //     } else {
            //     //         data[key] = selectField.value;
            //     //         localStorage.setItem('jsonData', JSON.stringify(jsonData));
            //     //     }
            //     // });
            //     // inputField.addEventListener('click', function (event) {
            //     //     event.stopPropagation();
            //     // });
            //     valueElement.appendChild(inputField);
            } else {                                                //другие поля (текстовые)
                const inputField = document.createElement('input');
                inputField.placeholder = 'Введите значение';
                inputField.type = 'text';
                inputField.value = data[key];
                inputField.className = 'input-field';
                inputField.readOnly = (!editableFields.includes(key));
                inputField.addEventListener('change', function () {
                    data[key] = inputField.value;
                    if (parentName === 'info') {
                        jsonData['scheme']['item_id_list'].forEach(item => {
                            if (item['full_path'] === data['full_path']) {
                                item['info'][key] = inputField.value;
                            }
                        });
                        updateLi(data, key, inputField.value);
                    } else if (chapter === 'item_info_list') {
                        changeField(chapter, data['full_path'], 'full_path', inputField.value, key);
                        updateInfoList(data, key, inputField.value);
                    }
                    localStorage.setItem('jsonData', JSON.stringify(jsonData));
                    if (key === 'name' && ['templates', 'metrics'].includes(chapter)) {
                        parent.querySelector('.key').textContent = inputField.value;
                    }
                });
                valueElement.appendChild(inputField);
            }
            listItem.appendChild(NameValue);
            listItem.appendChild(buttonGroup);
            listItem.appendChild(valueElement);
        }
        parentElement.appendChild(listItem);
    });
    updateButtonsState();
}

function changeField(chapter, id, id_name, newValue, field) { //изменение значение атрибута в схеме
    jsonData['scheme'][chapter].forEach(el => {
        if (el[id_name] === id) {
            el[field] = newValue;
        }
    });
}

function getType(value) {   //тип
    if (value === null) return 'null';
    if (Array.isArray(value)) return 'array';
    return typeof value;
}

function updateOpenedNodes(key, isOpen) { //обновление открытых вкладок
    if (isOpen && !openedNodes.includes(key)) {
        openedNodes.push(key);
    } else if (!isOpen) {
        openedNodes = openedNodes.filter(node => node !== key);
    }
    localStorage.setItem('openedNodes', JSON.stringify(openedNodes));
}

function addOptions(selector, options) { //Добавление опций к выпадающим спискам
    options.forEach(el => {
        const Option = document.createElement('option');
        Option.value = el;
        Option.textContent = el;
        selector.appendChild(Option);
    });
}

function getElement(chapter, full_path) { // получение элемента <li> из chapter по full_path
    let itemElToReturn;
    let liList = jsonTree.querySelectorAll('li');
    liList.forEach(li => {
        const liKey = li.querySelector('.key');
        if (liKey?.textContent === 'scheme') {
            const ulSchemeLiList = li.querySelector('ul')?.querySelectorAll('li') || [];
            ulSchemeLiList.forEach(liScheme => {
                const liSchemeKey = liScheme.querySelector('.key');
                if (liSchemeKey?.textContent === chapter) {
                    const itemList = liScheme.querySelector('ul')?.querySelectorAll('li') || [];
                    itemList.forEach(itemEl => {
                        const itemElKey = itemEl.querySelector('.key');
                        if (itemElKey?.textContent === full_path) {
                            itemElToReturn = itemEl;
                        }
                    });
                }
            });
        }
    });
    return itemElToReturn;
}

function updateLi(data, key, value) { // обновление дерева в item_info_list
    changeField('item_info_list', data['full_path'], 'full_path', value, key);
    let itemLi = getElement('item_info_list', data['full_path']);    
    const lastList = itemLi.querySelector('ul')?.querySelectorAll('li') || [];
    lastList.forEach(last => {
        const lastKey = last.querySelector('.key');
        if (lastKey?.textContent === key) {
            let vvod = last.querySelector('input.input-field'); 
            if (vvod === null) {
                vvod = last.querySelector('textarea.input-field');
            }
            vvod.value = value;
        }
    });
}

function updateInfoList(data, key, value) { // обновление дерева в item_id_list.info
    jsonData['scheme']['item_id_list'].forEach(item => {
        if (item['info'] && item['info']['full_path'] === data['full_path']) {
            item['info'][key] = value;
        }
    });

    let itemLi = getElement('item_id_list', data['full_path']);   
    const lastList = itemLi.querySelector('ul')?.querySelectorAll('li') || [];
    lastList.forEach(last => {
        const lastKey = last.querySelector('.key');
        if (lastKey?.textContent === 'info') {
            const trueLastList = last.querySelector('ul')?.querySelectorAll('li') || [];
            trueLastList.forEach(trueLast => {
                const trueLastKey = trueLast.querySelector('.key');
                if (trueLastKey?.textContent === key) {
                    trueLast.querySelector('input.input-field').value = value;
                }
            });
        }
    });
}

function plusButtonInfo(buttonGroup, full_path) {//создание и добавление кнопки + info
    const infoButton = document.createElement('span');
    infoButton.textContent = '+ info';
    infoButton.style.width = '45px';
    infoButton.className = 'add-btn';
    infoButton.addEventListener('click', function (event) { // Обработчик события нажатия кнопки + info
        event.stopPropagation();
        jsonData['scheme']['item_id_list'].forEach(item => {
            if (item['full_path'] === full_path) {
                item['info'] = { full_path: item['full_path'] };
            }
        });

        jsonData['scheme']['item_info_list'].push({ full_path: full_path });
        let liList = jsonTree.querySelectorAll('li');
        liList.forEach(li => {
            const liKey = li.querySelector('.key');
            if (liKey?.textContent === 'scheme') {
                const ulSchemeLiList = li.querySelector('ul')?.querySelectorAll('li') || [];
                ulSchemeLiList.forEach(liScheme => {
                    const liSchemeKey = liScheme.querySelector('.key');
                    if (liSchemeKey?.textContent === 'item_id_list') {
                        const itemList = liScheme.querySelector('ul')?.querySelectorAll('li') || [];
                        itemList.forEach(itemEl => {
                            const itemElKey = itemEl.querySelector('.key');
                            if (itemElKey?.textContent === full_path) {
                                itemEl.querySelector('.add-btn').remove();
                                let ul = itemEl.querySelector('ul');
                                renderJsonTree({ info: { full_path: full_path } }, ul, openedNodes, itemEl, 'item_id_list');
                            }
                        });
                    }
                    if (liSchemeKey?.textContent === 'item_info_list') {
                        let ul_ = liScheme.querySelector('ul');
                        renderJsonTree({ [full_path]: { full_path: full_path } }, ul_, openedNodes, liScheme, 'item_info_list');
                    }
                });
            }
        });
        localStorage.setItem('jsonData', JSON.stringify(jsonData));
    });
    buttonGroup.appendChild(infoButton);
}

function plusButtonField(button_field, buttonGroup, data) {     //создание и добавление кнопки + [имя_атрибута]
    if (!data[button_field] && (!["", false, 0].includes(data[button_field]))) {
        let button_width;
        switch (button_field) {
            case 'comment': {
                button_width = '77px'; break;
            }
            case 'name': {
                button_width = '55px'; break;
            }
            case 'sn': {
                button_width = '38px'; break;
            }
            case 'number': {
                button_width = '66px'; break;
            }
            default: { }
        }
        const addButton = document.createElement('span');
        addButton.textContent = '+ ' + button_field;
        addButton.style.width = button_width;
        addButton.className = 'add-btn';
        addButton.addEventListener('click', function (event) {// Обработчик события нажатия кнопки + [имя_атрибута]
            event.stopPropagation();

            jsonData['scheme']['item_info_list'].forEach(item => {
                if (item['full_path'] === data['full_path']) {
                    if (button_field !== 'number') {
                        item[button_field] = "";
                    } else {
                        item[button_field] = 0;
                    }
                }
            });
            jsonData['scheme']['item_id_list'].forEach(item => {
                if (item['full_path'] === data['full_path']) {
                    if (button_field !== 'number') {
                        item['info'][button_field] = "";
                    } else {
                        item['info'][button_field] = 0;
                    }
                }
            });
            let itemLi = getElement('item_info_list', data['full_path']);
            let btnGrInfo = itemLi.querySelector('.button-group'); 
            let itemUl = itemLi.querySelector('ul');
            let partOfTree = {};
            Array.from(itemUl.querySelectorAll('li')).find(li => li.querySelector('.key').textContent === 'full_path').remove();
            if (button_field === 'number') {
                partOfTree = { full_path: data['full_path'], number: 0 };
            } else {
                partOfTree = { full_path: data['full_path'], [button_field]: "" };
            }
            renderJsonTree(partOfTree, itemUl, openedNodes, itemLi, 'item_info_list');

            let btnGrId;
            let itemLiId = getElement('item_id_list', data['full_path']);            
            let itemUlId = itemLiId.querySelector('ul');
            const itemList = itemUlId?.querySelectorAll('li') || [];
            itemList.forEach(itemEl => {
                const itemElKey = itemEl.querySelector('.key');
                if (itemElKey?.textContent === 'info') {
                    btnGrId = itemEl.querySelector('.button-group');
                    let itemElUl = itemEl.querySelector('ul');
                    Array.from(itemElUl.querySelectorAll('li')).find(li => li.querySelector('.key').textContent === 'full_path').remove();
                    renderJsonTree(partOfTree, itemElUl, openedNodes, itemEl, 'item_id_list');
                }
            });
            if (btnGrId && btnGrInfo) {
                Array.from(btnGrInfo.querySelectorAll('.add-btn')).find(btn => btn.textContent.trim() === '+ ' + button_field).remove();
                Array.from(btnGrId.querySelectorAll('.add-btn')).find(btn => btn.textContent.trim() === '+ ' + button_field).remove();
            }
            localStorage.setItem('jsonData', JSON.stringify(jsonData));
        });
        addElementToStart(buttonGroup, addButton);
    }
}

function delete_button(buttonGroup, data, key, parentName) { //создание и добавление кнопки (х)
    const deleteButton = document.createElement('span');
    deleteButton.textContent = '×';
    deleteButton.className = 'delete-btn';
    deleteButton.addEventListener('click', function (event) {// Обработчик события нажатия кнопки (х)
        event.stopPropagation();
        let full_path;

        if (parentName === 'item_info_list') {
            full_path = data[key]['full_path'];
        } else {
            full_path = data['full_path'];
            if (!full_path) { full_path = data[key]['full_path']; }
        }
        let itemInfo = getElement('item_info_list', full_path);
        let itemId = getElement('item_id_list', full_path);        
        if (parentName === 'item_info_list' || key === 'info') {
            jsonData['scheme']['item_info_list'] = jsonData['scheme']['item_info_list'].filter(obj => obj['full_path'] !== full_path);
            jsonData['scheme']['item_id_list'].forEach(item => {
                if (item['full_path'] === full_path) {
                    delete item['info'];
                }
            });
            itemInfo.remove();
            Array.from(itemId.querySelector('ul')?.querySelectorAll('li')).find(li => li.querySelector('.key').textContent === 'info').remove();
            let btnGrp = itemId.querySelector('.button-group');
            plusButtonInfo(btnGrp, full_path, key);
        } else {
            let dataForButtons;
            jsonData['scheme']['item_info_list'].forEach(item => {
                if (item['full_path'] === full_path) {
                    delete item[key];
                    dataForButtons = item;
                }
            });
            jsonData['scheme']['item_id_list'].forEach(item => {
                if (item['full_path'] === full_path) {
                    delete item['info'][key];                    
                }
            });            
            Array.from(itemInfo.querySelector('ul')?.querySelectorAll('li')).find(li => li.querySelector('.key').textContent === key).remove();            
            let infoUl = Array.from(itemId.querySelector('ul')?.querySelectorAll('li')).find(li => li.querySelector('.key').textContent === 'info');
            Array.from(infoUl.querySelector('ul')?.querySelectorAll('li')).find(li => li.querySelector('.key').textContent === key).remove();       

            let btnGrpInfo = itemInfo.querySelector('.button-group');
            let btnGrpId = Array.from(itemId.querySelector('ul')?.querySelectorAll('li')).find(li => li.querySelector('.key').textContent === 'info').querySelector('.button-group');
            plusButtonField(key, btnGrpInfo, dataForButtons);
            plusButtonField(key, btnGrpId, dataForButtons);
        }
        localStorage.setItem('jsonData', JSON.stringify(jsonData));
    });
    buttonGroup.appendChild(deleteButton);
}

function addElementToStart(container, newElement) { //правильный порядок добавления кнопок
    if (container.firstChild) { 
        container.insertBefore(newElement, container.firstChild);
    } else {
        container.appendChild(newElement); 
    }
}