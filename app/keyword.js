module.exports = function check_content(content){
  const forbidden_words = [
    '://ais',
    'www.ais',
    '增粉',
    '拉粉',
    '加粉',
    '炸群',
    'XackerTVHD',
    'ad84',
    '交友粉',
    '科技引流'
  ]
  const checkRe = new RegExp(forbidden_words.join('|'))
  return checkRe.test(content)
}

console.log(check_content('我要炸群拉粉'))