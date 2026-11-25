import { createI18n } from 'vue-i18n'

// UI chrome is translated (navigation, headings, buttons, key messages). Opportunity content comes
// from official sources and is shown as published; Saathi AI can explain it in Hindi or Marathi.
const en = {
  nav: { home: 'Home', explore: 'Explore Opportunities', how: 'How It Works', about: 'About', login: 'Log in', start: 'Get Started', dashboard: 'Dashboard', discover: 'Discover', saved: 'Saved', tracker: 'Tracker', calendar: 'Calendar', documents: 'Documents', saathi: 'Saathi AI', resume: 'Resume builder', notifications: 'Notifications', profile: 'Profile', settings: 'Settings', admin: 'Admin', logout: 'Log out', more: 'More' },
  hero: { title1: 'Your Next Opportunity', title2: 'Starts Here.', sub: "Discover opportunities you're eligible for, understand every requirement, and complete applications with confidence.", search: 'Try “engineering scholarship” or “internship”', explore: 'Explore Opportunities', start: 'Get Started — it’s free' },
  common: { save: 'Save', saved: 'Saved', cancel: 'Cancel', continue: 'Continue', back: 'Back', search: 'Search', viewAll: 'View all', loading: 'Loading…', retry: 'Try again', track: 'Track application', checkEligibility: 'Check my eligibility', officialSite: 'Official website', apply: 'Apply on official site', demo: 'Demo', verified: 'Verified', pending: 'Pending verification', expired: 'Expired', ai: 'AI guidance', skip: 'Skip for now', finish: 'Finish', edit: 'Edit', delete: 'Delete', close: 'Close', filters: 'Filters', clear: 'Clear all' },
  dash: { welcome: 'Welcome back, {name}', sub: "Here's what needs your attention today.", recommended: 'Recommended for you', deadlines: 'Upcoming deadlines', progress: 'Application progress', pendingDocs: 'Pending documents', quick: 'Quick actions', activity: 'This week', completion: 'Profile completion', recent: 'Recently added' },
  footer: { tagline: 'Never Miss an Opportunity You Deserve.' },
}

const hi = {
  nav: { home: 'होम', explore: 'अवसर खोजें', how: 'यह कैसे काम करता है', about: 'हमारे बारे में', login: 'लॉग इन', start: 'शुरू करें', dashboard: 'डैशबोर्ड', discover: 'खोजें', saved: 'सहेजे गए', tracker: 'ट्रैकर', calendar: 'कैलेंडर', documents: 'दस्तावेज़', saathi: 'साथी AI', resume: 'रिज़्यूमे बिल्डर', notifications: 'सूचनाएँ', profile: 'प्रोफ़ाइल', settings: 'सेटिंग्स', admin: 'एडमिन', logout: 'लॉग आउट', more: 'और' },
  hero: { title1: 'आपका अगला अवसर', title2: 'यहीं से शुरू होता है।', sub: 'जिन अवसरों के लिए आप पात्र हैं उन्हें खोजें, हर ज़रूरत को समझें, और आत्मविश्वास से आवेदन पूरा करें।', search: '“इंजीनियरिंग छात्रवृत्ति” या “इंटर्नशिप” खोजें', explore: 'अवसर खोजें', start: 'शुरू करें — मुफ़्त है' },
  common: { save: 'सहेजें', saved: 'सहेजा गया', cancel: 'रद्द करें', continue: 'आगे बढ़ें', back: 'पीछे', search: 'खोजें', viewAll: 'सभी देखें', loading: 'लोड हो रहा है…', retry: 'फिर कोशिश करें', track: 'आवेदन ट्रैक करें', checkEligibility: 'मेरी पात्रता जाँचें', officialSite: 'आधिकारिक वेबसाइट', apply: 'आधिकारिक साइट पर आवेदन करें', demo: 'डेमो', verified: 'सत्यापित', pending: 'सत्यापन बाकी', expired: 'समाप्त', ai: 'AI मार्गदर्शन', skip: 'अभी छोड़ें', finish: 'पूरा करें', edit: 'बदलें', delete: 'हटाएँ', close: 'बंद करें', filters: 'फ़िल्टर', clear: 'सब हटाएँ' },
  dash: { welcome: 'फिर से स्वागत है, {name}', sub: 'आज इन पर ध्यान दें।', recommended: 'आपके लिए सुझाव', deadlines: 'आने वाली अंतिम तिथियाँ', progress: 'आवेदन की प्रगति', pendingDocs: 'बाकी दस्तावेज़', quick: 'त्वरित कार्य', activity: 'इस सप्ताह', completion: 'प्रोफ़ाइल पूर्णता', recent: 'हाल ही में जोड़े गए' },
  footer: { tagline: 'कोई भी हक़ का अवसर न छूटे।' },
}

const mr = {
  nav: { home: 'मुख्यपृष्ठ', explore: 'संधी शोधा', how: 'हे कसे काम करते', about: 'आमच्याबद्दल', login: 'लॉग इन', start: 'सुरू करा', dashboard: 'डॅशबोर्ड', discover: 'शोधा', saved: 'जतन केलेले', tracker: 'ट्रॅकर', calendar: 'दिनदर्शिका', documents: 'कागदपत्रे', saathi: 'साथी AI', resume: 'रेझ्युमे बिल्डर', notifications: 'सूचना', profile: 'प्रोफाइल', settings: 'सेटिंग्ज', admin: 'अ‍ॅडमिन', logout: 'लॉग आउट', more: 'अधिक' },
  hero: { title1: 'तुमची पुढची संधी', title2: 'इथून सुरू होते.', sub: 'तुम्ही पात्र असलेल्या संधी शोधा, प्रत्येक अट समजून घ्या आणि आत्मविश्वासाने अर्ज पूर्ण करा.', search: '“अभियांत्रिकी शिष्यवृत्ती” किंवा “इंटर्नशिप” शोधा', explore: 'संधी शोधा', start: 'सुरू करा — मोफत' },
  common: { save: 'जतन करा', saved: 'जतन केले', cancel: 'रद्द करा', continue: 'पुढे चला', back: 'मागे', search: 'शोधा', viewAll: 'सर्व पहा', loading: 'लोड होत आहे…', retry: 'पुन्हा प्रयत्न करा', track: 'अर्ज ट्रॅक करा', checkEligibility: 'माझी पात्रता तपासा', officialSite: 'अधिकृत संकेतस्थळ', apply: 'अधिकृत साइटवर अर्ज करा', demo: 'डेमो', verified: 'पडताळलेले', pending: 'पडताळणी बाकी', expired: 'मुदत संपली', ai: 'AI मार्गदर्शन', skip: 'आता वगळा', finish: 'पूर्ण करा', edit: 'बदला', delete: 'हटवा', close: 'बंद करा', filters: 'फिल्टर', clear: 'सर्व काढा' },
  dash: { welcome: 'पुन्हा स्वागत, {name}', sub: 'आज याकडे लक्ष द्या.', recommended: 'तुमच्यासाठी सुचवलेले', deadlines: 'येणाऱ्या अंतिम तारखा', progress: 'अर्जाची प्रगती', pendingDocs: 'बाकी कागदपत्रे', quick: 'झटपट कृती', activity: 'या आठवड्यात', completion: 'प्रोफाइल पूर्णता', recent: 'नुकतेच जोडलेले' },
  footer: { tagline: 'तुमच्या हक्काची एकही संधी चुकवू नका.' },
}

export const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('fs-lang') || 'en',
  fallbackLocale: 'en',
  messages: { en, hi, mr },
})

export function setLanguage(lang) {
  i18n.global.locale.value = lang
  localStorage.setItem('fs-lang', lang)
  document.documentElement.setAttribute('lang', lang)
}
