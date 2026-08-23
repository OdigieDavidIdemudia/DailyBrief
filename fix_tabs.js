const fs = require('fs');
const path = 'c:/Users/DELL/OneDrive/Documents/New folder/THolder/frontend/src/pages/Configure.jsx';

let content = fs.readFileSync(path, 'utf8');

content = content.replace(
    "className={px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors }",
    "className={`px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors ${activeTab === 'blueprints' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}"
);

content = content.replace(
    "className={px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors }",
    "className={`px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors ${activeTab === 'ai_engine' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}"
);

content = content.replace(
    "className={px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors }",
    "className={`px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors ${activeTab === 'integrations' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}"
);

fs.writeFileSync(path, content);
console.log("Fixed Configure.jsx");
