import { describe, expect, it } from 'vitest'
import { evaluate } from './eligibility.js'

const year = new Date().getFullYear()
const p = { date_of_birth: `${year - 20}-01-01`, education_level: 'undergraduate', course: 'B.Tech Computer', marks_type: 'percentage', marks_value: 72, income_range: '1l_to_2_5l', state_code: 'maharashtra', gender: 'female' }
const c = (criterion_type, value, is_mandatory = true) => ({ criterion_type, value, description: 'rule', is_mandatory })

describe('preview eligibility engine (mirror of the Python engine)', () => {
  it('all met -> eligible', () => {
    expect(evaluate(p, [c('education_level', { any_of: ['undergraduate'] }), c('income_max', { amount: 250000 }), c('age_max', { years: 25 })]).verdict).toBe('eligible')
  })
  it('mandatory not met -> not eligible', () => {
    expect(evaluate({ ...p, education_level: 'class_12' }, [c('education_level', { any_of: ['undergraduate'] })]).verdict).toBe('not_eligible')
  })
  it('missing data -> possibly eligible with missing field', () => {
    const r = evaluate({ ...p, social_category: null }, [c('social_category', { any_of: ['sc'] })])
    expect(r.verdict).toBe('possibly_eligible')
    expect(r.missing_fields).toEqual(['social_category'])
  })
  it('custom rules always need review', () => {
    expect(evaluate(p, [c('custom', {})]).results[0].outcome).toBe('needs_review')
  })
  it('income bands', () => {
    expect(evaluate({ ...p, income_range: '5l_to_8l' }, [c('income_max', { amount: 250000 })]).verdict).toBe('not_eligible')
    expect(evaluate({ ...p, income_range: '2_5l_to_5l' }, [c('income_max', { amount: 300000 })]).results[0].outcome).toBe('unknown')
  })
  it('does not convert CGPA to percentage', () => {
    expect(evaluate({ ...p, marks_type: 'cgpa', marks_value: 8 }, [c('marks_min_percentage', { value: 60 })]).results[0].outcome).toBe('needs_review')
  })
})
