const knex = require('./knex');

module.exports = function Model(table){
  return {
    'save': async (payload, identifier=['id']) => {
      const filter = identifier.reduce((o, k) => ({...o, [k]: payload[k]}), {})
      let entity = await knex(table).where(filter).first()
      if(!entity){
        entity = await knex(table).insert(payload).returning('*')
      }
      return entity
    }
  }
}