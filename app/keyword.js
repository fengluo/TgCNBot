module.exports = function checkContent(content, type='message'){
  const forbiddenWords = [
    '://ais',
    'www.ais',
    '增粉',
    '拉粉',
    '加粉',
    '炸群',
    'XackerTVHD',
    'ad84',
    'ad83',
    'ad82',
    '交友粉',
    '科技引流',
    'hch677'
  ]
  const forbiddenWordsForName = [
    'Deleted Account',
    '反水',
    '分红',
    '炸群'
  ]
  const checkRe = type === 'message' ? new RegExp(forbiddenWords.join('|')) : new RegExp(forbiddenWordsForName.join('|'))
  return checkRe.test(content)
}

// console.log(checkContent('我要炸群拉粉'))