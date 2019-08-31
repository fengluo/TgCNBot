module.exports = function checkContent(content){
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
    '科技引流'
  ]
  const checkRe = new RegExp(forbiddenWords.join('|'))
  return checkRe.test(content)
}

// console.log(checkContent('我要炸群拉粉'))