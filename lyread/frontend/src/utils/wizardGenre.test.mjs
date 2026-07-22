/**
 * Lightweight Node smoke test for wizardGenre helpers (no Vite required).
 * Run: node lyread/frontend/src/utils/wizardGenre.test.mjs
 */
import {
  GENRE_NAME_BY_ID,
  wizardGenreFromCategory,
  workspaceWizardQuery,
  workspaceTrialQuery,
} from './wizardGenre.js'

function assert(cond, msg) {
  if (!cond) throw new Error(msg)
}

assert(wizardGenreFromCategory('urban').type === 'urban', 'english id urban')
assert(wizardGenreFromCategory('都市神豪').type === 'urban', 'chinese urban')
assert(wizardGenreFromCategory('战神归来').type === 'warrior', 'chinese warrior')
assert(GENRE_NAME_BY_ID.fantasy === '玄幻修仙', 'genre name map')

const trial = workspaceTrialQuery({
  type: 'fantasy',
  prompt: '废柴逆袭成仙',
  title: '开局一条狗',
})
assert(trial.mode === 'new', 'trial mode=new')
assert(trial.type === 'fantasy', 'trial type')
assert(trial.genreName === '玄幻修仙', 'trial genreName')
assert(trial.generatedTitle === '开局一条狗', 'trial title')
assert(trial.prompt.includes('废柴'), 'trial prompt')

const empty = workspaceTrialQuery({})
assert(empty.mode === 'new', 'empty still mode=new')
assert(!empty.type && !empty.prompt, 'empty omits blanks')

const same = workspaceWizardQuery({ category: '都市', title: '开局十个亿' })
assert(same.mode === 'new' && same.type === 'urban', 'wizard query urban')
assert(same.prompt.includes('开局十个亿'), 'wizard prompt refs title')

console.log('wizardGenre.test.mjs: ok')
