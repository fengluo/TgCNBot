module.exports = function checkContent(content, type='message'){
  const forbiddenWords = [
    '://ais',
    'www.ais',
    '增粉',
    '拉粉',
    '加粉',
    '炸群',
    'XackerTVHD',
    '交友粉',
    '科技引流',
    'hch677',
    'wodeai.cn',
    '精准粉'
  ]
  const forbiddenWordsForName = forbiddenWords.concat([
    'Deleted Account',
    '反水',
    '分红'
  ])
  const checkRe = type === 'message' ? new RegExp(forbiddenWords.join('|')) : new RegExp(forbiddenWordsForName.join('|'))
  return checkRe.test(content)
}

// console.log(checkContent('我要炸群拉粉'))
