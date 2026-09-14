import React, { useState, useEffect } from 'react';
import { Archive, Download, Trash2, Search, Clock, File } from 'lucide-react';

const API = "";

const Repository = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchDocs();
  }, []);

  const fetchDocs = async () => {
    try {
      const res = await fetch(`${API}/api/repository/list`, { credentials: 'include' });
      if (res.ok) {
        setDocuments(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if(!window.confirm("Are you sure you want to delete this document?")) return;
    try {
      await fetch(`${API}/api/repository/${id}`, { method: 'DELETE', credentials: 'include' });
      fetchDocs();
    } catch(e) { console.error(e); }
  };

  const handleDownload = (doc) => {
    const url = doc.file_path.startsWith('http') ? doc.file_path : `${API}/${doc.file_path.replace(/\\/g, '/')}`;
    window.open(url, '_blank');
  };

  const filteredDocs = documents.filter(d => d.title.toLowerCase().includes(search.toLowerCase()) || d.module.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-neo-yellow p-6 rounded-neo border-neo border-neo-border shadow-neo gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-wider">Repository</h1>
          <p className="font-bold border-t-2 border-black pt-1 mt-1">ACCESS AND MANAGE YOUR SAVED REPORTS.</p>
        </div>
      </div>

      <div className="flex bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 text-black w-5 h-5" />
          <input 
            type="text" 
            placeholder="Search documents by title or module..." 
            className="neo-input pl-10 text-lg"
            value={search} 
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-12 w-12 border-4 border-neo-primary border-t-transparent"></div></div>
      ) : filteredDocs.length === 0 ? (
        <div className="text-center py-24 bg-white border-neo border-neo-border rounded-neo shadow-neo">
          <File className="h-20 w-20 mx-auto opacity-20 mb-4 text-black" strokeWidth={2} />
          <h3 className="text-2xl font-black uppercase text-gray-500">NO DOCUMENTS FOUND</h3>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredDocs.map(doc => (
            <div key={doc.id} className="neo-card flex flex-col hover:-translate-y-1 transition-transform group">
              <div className="bg-neo-blue p-4 border-b-neo border-neo-border flex justify-between items-center group-hover:bg-neo-primary group-hover:text-white transition-colors">
                <div className="flex items-center gap-3">
                  <File className="h-6 w-6" strokeWidth={3} />
                  <span className="font-bold text-lg leading-tight uppercase">{doc.module}</span>
                </div>
              </div>
              <div className="p-4 space-y-4 bg-white flex-1 flex flex-col">
                <div>
                  <h4 className="font-black text-xl uppercase mb-1">{doc.title}</h4>
                  <p className="text-xs font-bold text-gray-500 flex items-center gap-1 uppercase">
                    <Clock className="w-3 h-3"/> {new Date(doc.date_generated).toLocaleDateString()}
                  </p>
                </div>
                
                <div className="flex gap-2 mt-auto pt-4 border-t-2 border-dashed border-gray-300">
                  <button onClick={() => handleDownload(doc)} className="neo-btn flex-1 flex items-center justify-center gap-2">
                    <Download className="w-4 h-4" /> Download
                  </button>
                  <button onClick={() => handleDelete(doc.id)} className="neo-btn-accent px-3">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
export default Repository;

