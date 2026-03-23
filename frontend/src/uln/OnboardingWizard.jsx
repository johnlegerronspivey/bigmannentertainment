import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Check, ChevronRight, ChevronLeft, Building, FileText, Users, Shield, ClipboardCheck } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const getToken = () => localStorage.getItem('token');

const STEPS = [
  { step: 1, title: 'Basic Information', icon: <Building className="w-5 h-5" />, desc: 'Label name, type, and location' },
  { step: 2, title: 'Business Details', icon: <FileText className="w-5 h-5" />, desc: 'Legal and tax information' },
  { step: 3, title: 'Key Personnel', icon: <Users className="w-5 h-5" />, desc: 'Team members and roles' },
  { step: 4, title: 'Smart Contract', icon: <Shield className="w-5 h-5" />, desc: 'Blockchain configuration' },
  { step: 5, title: 'Review & Submit', icon: <ClipboardCheck className="w-5 h-5" />, desc: 'Confirm and register' },
];

const LABEL_TYPES = ['major', 'independent', 'distribution', 'publishing', 'management'];
const JURISDICTIONS = ['US', 'UK', 'EU', 'CA', 'AU', 'JP', 'GLOBAL'];
const CONTRACT_TYPES = ['rights_split', 'royalty_distribution', 'dao_governance', 'licensing'];

export const OnboardingWizard = () => {
  const [sessionId, setSessionId] = useState(null);
  const [currentStep, setCurrentStep] = useState(0); // 0 = not started
  const [formData, setFormData] = useState({
    step_1: { name: '', label_type: 'independent', jurisdiction: 'US', headquarters: '', integration_type: 'api_partner', genres: [], territories: [] },
    step_2: { legal_name: '', tax_status: 'llc', business_registration_number: '', tax_id: '', founded_date: '' },
    step_3: { entities: [{ name: '', role: '', entity_type: 'admin', permissions: ['full_access'] }] },
    step_4: { contract_type: 'rights_split', rights_splits: { master_rights: 70, publishing_rights: 15, distribution_rights: 15 }, dao_integration: false },
  });
  const [saving, setSaving] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [result, setResult] = useState(null);
  const [genreInput, setGenreInput] = useState('');

  const startOnboarding = async () => {
    const res = await fetch(`${API}/api/uln-enhanced/onboarding/start`, {
      method: 'POST', headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    if (data.success) {
      setSessionId(data.session_id);
      setCurrentStep(1);
    }
  };

  const saveStep = async (step) => {
    setSaving(true);
    const res = await fetch(`${API}/api/uln-enhanced/onboarding/${sessionId}/step`, {
      method: 'POST', headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ step, data: formData[`step_${step}`] }),
    });
    const data = await res.json();
    setSaving(false);
    if (data.success) setCurrentStep(data.next_step);
  };

  const completeOnboarding = async () => {
    setSaving(true);
    const res = await fetch(`${API}/api/uln-enhanced/onboarding/${sessionId}/complete`, {
      method: 'POST', headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    setSaving(false);
    if (data.success) {
      setCompleted(true);
      setResult(data.registration_payload);
    }
  };

  const updateField = (step, field, value) => {
    setFormData((prev) => ({ ...prev, [`step_${step}`]: { ...prev[`step_${step}`], [field]: value } }));
  };

  const addGenre = () => {
    if (genreInput.trim()) {
      updateField(1, 'genres', [...(formData.step_1.genres || []), genreInput.trim()]);
      setGenreInput('');
    }
  };

  const addEntity = () => {
    setFormData((prev) => ({
      ...prev, step_3: { ...prev.step_3, entities: [...prev.step_3.entities, { name: '', role: '', entity_type: 'admin', permissions: ['full_access'] }] },
    }));
  };

  const updateEntity = (idx, field, value) => {
    const entities = [...formData.step_3.entities];
    entities[idx] = { ...entities[idx], [field]: value };
    setFormData((prev) => ({ ...prev, step_3: { ...prev.step_3, entities } }));
  };

  // Not started state
  if (currentStep === 0) {
    return (
      <div className="max-w-2xl mx-auto" data-testid="onboarding-wizard">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-8 text-center space-y-6">
            <div className="w-16 h-16 mx-auto rounded-full bg-violet-500/20 flex items-center justify-center">
              <Building className="w-8 h-8 text-violet-400" />
            </div>
            <h2 className="text-2xl font-bold text-white">Register a New Label</h2>
            <p className="text-slate-400">Walk through our guided 5-step process to register your label in the Unified Label Network. You'll set up your profile, business details, team, and blockchain configuration.</p>
            <div className="flex justify-center gap-2">
              {STEPS.map((s) => (
                <div key={s.step} className="flex items-center gap-1 text-xs text-slate-500">
                  <span className="w-6 h-6 rounded-full border border-slate-600 flex items-center justify-center">{s.step}</span>
                  <span className="hidden md:inline">{s.title}</span>
                  {s.step < 5 && <ChevronRight className="w-3 h-3 text-slate-600" />}
                </div>
              ))}
            </div>
            <Button onClick={startOnboarding} className="bg-violet-600 hover:bg-violet-700 px-8" data-testid="start-onboarding-btn">
              Begin Registration
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Completed
  if (completed) {
    return (
      <div className="max-w-2xl mx-auto" data-testid="onboarding-complete">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-8 text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/20 flex items-center justify-center">
              <Check className="w-8 h-8 text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold text-white">Registration Complete</h2>
            <p className="text-slate-400">Your label has been submitted for registration in the Unified Label Network.</p>
            {result && (
              <div className="text-left bg-slate-700/50 rounded-lg p-4 mt-4">
                <p className="text-sm text-slate-400 mb-2">Registration Summary:</p>
                <p className="text-white"><strong>Label:</strong> {result.metadata_profile?.name}</p>
                <p className="text-white"><strong>Type:</strong> {result.label_type}</p>
                <p className="text-white"><strong>Territory:</strong> {result.metadata_profile?.jurisdiction}</p>
              </div>
            )}
            <Button onClick={() => { setCurrentStep(0); setCompleted(false); setSessionId(null); setResult(null); }} variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700">
              Register Another Label
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Step progress
  return (
    <div className="max-w-3xl mx-auto space-y-6" data-testid="onboarding-wizard">
      {/* Progress bar */}
      <div className="flex items-center gap-1">
        {STEPS.map((s) => (
          <React.Fragment key={s.step}>
            <button onClick={() => s.step < currentStep && setCurrentStep(s.step)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                s.step === currentStep ? 'bg-violet-600 text-white' : s.step < currentStep ? 'bg-violet-900/40 text-violet-400 cursor-pointer' : 'bg-slate-700/50 text-slate-500'
              }`}>
              {s.step < currentStep ? <Check className="w-4 h-4" /> : s.icon}
              <span className="hidden sm:inline">{s.title}</span>
            </button>
            {s.step < 5 && <ChevronRight className="w-4 h-4 text-slate-600 shrink-0" />}
          </React.Fragment>
        ))}
      </div>

      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">{STEPS[currentStep - 1]?.title}</CardTitle>
          <p className="text-sm text-slate-400">{STEPS[currentStep - 1]?.desc}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Step 1 */}
          {currentStep === 1 && (
            <>
              <div><label className="text-sm text-slate-400 block mb-1">Label Name *</label>
                <Input placeholder="e.g. Midnight Records" value={formData.step_1.name} onChange={(e) => updateField(1, 'name', e.target.value)} className="bg-slate-700 border-slate-600 text-white" data-testid="onboarding-name" /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-sm text-slate-400 block mb-1">Label Type</label>
                  <select value={formData.step_1.label_type} onChange={(e) => updateField(1, 'label_type', e.target.value)} className="w-full bg-slate-700 border border-slate-600 text-white rounded px-3 py-2 text-sm">
                    {LABEL_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                  </select></div>
                <div><label className="text-sm text-slate-400 block mb-1">Jurisdiction</label>
                  <select value={formData.step_1.jurisdiction} onChange={(e) => updateField(1, 'jurisdiction', e.target.value)} className="w-full bg-slate-700 border border-slate-600 text-white rounded px-3 py-2 text-sm">
                    {JURISDICTIONS.map((j) => <option key={j} value={j}>{j}</option>)}
                  </select></div>
              </div>
              <div><label className="text-sm text-slate-400 block mb-1">Headquarters</label>
                <Input placeholder="e.g. Los Angeles, CA" value={formData.step_1.headquarters} onChange={(e) => updateField(1, 'headquarters', e.target.value)} className="bg-slate-700 border-slate-600 text-white" /></div>
              <div><label className="text-sm text-slate-400 block mb-1">Genres</label>
                <div className="flex gap-2">
                  <Input placeholder="Add genre" value={genreInput} onChange={(e) => setGenreInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addGenre())} className="bg-slate-700 border-slate-600 text-white" />
                  <Button onClick={addGenre} variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700 shrink-0">Add</Button>
                </div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {formData.step_1.genres.map((g, i) => (
                    <span key={i} className="px-2 py-1 text-xs rounded bg-violet-900/40 text-violet-400 cursor-pointer" onClick={() => updateField(1, 'genres', formData.step_1.genres.filter((_, j) => j !== i))}>{g} x</span>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Step 2 */}
          {currentStep === 2 && (
            <>
              <div><label className="text-sm text-slate-400 block mb-1">Legal Name</label>
                <Input placeholder="Full legal entity name" value={formData.step_2.legal_name} onChange={(e) => updateField(2, 'legal_name', e.target.value)} className="bg-slate-700 border-slate-600 text-white" /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-sm text-slate-400 block mb-1">Tax Status</label>
                  <select value={formData.step_2.tax_status} onChange={(e) => updateField(2, 'tax_status', e.target.value)} className="w-full bg-slate-700 border border-slate-600 text-white rounded px-3 py-2 text-sm">
                    <option value="llc">LLC</option><option value="corporation">Corporation</option><option value="sole_proprietorship">Sole Proprietorship</option><option value="partnership">Partnership</option>
                  </select></div>
                <div><label className="text-sm text-slate-400 block mb-1">Founded Date</label>
                  <Input type="date" value={formData.step_2.founded_date} onChange={(e) => updateField(2, 'founded_date', e.target.value)} className="bg-slate-700 border-slate-600 text-white" /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><label className="text-sm text-slate-400 block mb-1">Registration #</label>
                  <Input placeholder="Business reg number" value={formData.step_2.business_registration_number} onChange={(e) => updateField(2, 'business_registration_number', e.target.value)} className="bg-slate-700 border-slate-600 text-white" /></div>
                <div><label className="text-sm text-slate-400 block mb-1">Tax ID</label>
                  <Input placeholder="Tax identification" value={formData.step_2.tax_id} onChange={(e) => updateField(2, 'tax_id', e.target.value)} className="bg-slate-700 border-slate-600 text-white" /></div>
              </div>
            </>
          )}

          {/* Step 3 */}
          {currentStep === 3 && (
            <>
              {formData.step_3.entities.map((ent, i) => (
                <div key={i} className="p-4 rounded-lg bg-slate-700/50 space-y-3">
                  <div className="flex justify-between items-center"><span className="text-sm text-slate-400">Person {i + 1}</span>
                    {i > 0 && <button className="text-xs text-red-400 hover:text-red-300" onClick={() => setFormData((p) => ({ ...p, step_3: { ...p.step_3, entities: p.step_3.entities.filter((_, j) => j !== i) } }))}>Remove</button>}
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Input placeholder="Full name" value={ent.name} onChange={(e) => updateEntity(i, 'name', e.target.value)} className="bg-slate-700 border-slate-600 text-white" />
                    <Input placeholder="Role (e.g. CEO, A&R)" value={ent.role} onChange={(e) => updateEntity(i, 'role', e.target.value)} className="bg-slate-700 border-slate-600 text-white" />
                  </div>
                </div>
              ))}
              <Button onClick={addEntity} variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700 w-full">+ Add Another Person</Button>
            </>
          )}

          {/* Step 4 */}
          {currentStep === 4 && (
            <>
              <div><label className="text-sm text-slate-400 block mb-1">Contract Type</label>
                <select value={formData.step_4.contract_type} onChange={(e) => updateField(4, 'contract_type', e.target.value)} className="w-full bg-slate-700 border border-slate-600 text-white rounded px-3 py-2 text-sm">
                  {CONTRACT_TYPES.map((t) => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
                </select></div>
              <div><label className="text-sm text-slate-400 block mb-1">Rights Splits (%)</label>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(formData.step_4.rights_splits).map(([k, v]) => (
                    <div key={k}><label className="text-xs text-slate-500 capitalize">{k.replace(/_/g, ' ')}</label>
                      <Input type="number" min={0} max={100} value={v} onChange={(e) => updateField(4, 'rights_splits', { ...formData.step_4.rights_splits, [k]: Number(e.target.value) })} className="bg-slate-700 border-slate-600 text-white" /></div>
                  ))}
                </div>
              </div>
              <label className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" checked={formData.step_4.dao_integration} onChange={(e) => updateField(4, 'dao_integration', e.target.checked)} className="w-4 h-4 rounded bg-slate-700 border-slate-600" />
                <span className="text-sm text-slate-300">Enable DAO Governance Integration</span>
              </label>
            </>
          )}

          {/* Step 5 - Review */}
          {currentStep === 5 && (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-slate-700/50">
                <p className="text-xs text-slate-500 mb-1">Label</p>
                <p className="text-white font-medium">{formData.step_1.name || '(not set)'} — {formData.step_1.label_type}</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-700/50">
                <p className="text-xs text-slate-500 mb-1">Business</p>
                <p className="text-white">{formData.step_2.legal_name || formData.step_1.name} | Tax: {formData.step_2.tax_status}</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-700/50">
                <p className="text-xs text-slate-500 mb-1">Team</p>
                <p className="text-white">{formData.step_3.entities.length} members: {formData.step_3.entities.map((e) => e.name || '(unnamed)').join(', ')}</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-700/50">
                <p className="text-xs text-slate-500 mb-1">Smart Contract</p>
                <p className="text-white">{formData.step_4.contract_type.replace(/_/g, ' ')} | DAO: {formData.step_4.dao_integration ? 'Yes' : 'No'}</p>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between pt-4">
            <Button onClick={() => setCurrentStep((s) => Math.max(1, s - 1))} disabled={currentStep === 1} variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-700">
              <ChevronLeft className="w-4 h-4 mr-1" /> Back
            </Button>
            {currentStep < 5 ? (
              <Button onClick={() => saveStep(currentStep)} disabled={saving} className="bg-violet-600 hover:bg-violet-700" data-testid="next-step-btn">
                {saving ? 'Saving...' : 'Next'} <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            ) : (
              <Button onClick={completeOnboarding} disabled={saving} className="bg-emerald-600 hover:bg-emerald-700" data-testid="complete-onboarding-btn">
                {saving ? 'Submitting...' : 'Complete Registration'} <Check className="w-4 h-4 ml-1" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
