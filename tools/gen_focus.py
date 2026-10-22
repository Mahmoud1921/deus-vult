# Writes the focus trees for the European powers, Byzantium, Rum and the Papacy,
# plus a medieval tree shared by every nation without its own.
# Jerusalem and the Ayyubids are in gen_content.py; this script uses its ideas,
# opinions and holy war mechanics (dv_crusader_vow, dv_jihad, dv_<religion>).
# Usage: python3 gen_focus.py <mod folder>
import os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
LOC = []
T3 = '\t\t\t'
MIL = ['FOCUS_FILTER_MILITARY']
IND = ['FOCUS_FILTER_INDUSTRY']
RES = ['FOCUS_FILTER_RESEARCH']


def w(path, text, bom=False):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='\n').write(text)


def loc(key, text):
    LOC.append(f' {key}:0 "{text}"')


def ind(text, tabs=T3):
    return ''.join(f'{tabs}{l}\n' if l else '\n' for l in text.strip('\n').split('\n'))


# ---------------------------------------------------------------- ideas granted by these focuses
IDEAS = {
    'dv_crusader_king': ('Crusader King', 'Our king has fought in the Holy Land, and every knight in the realm wants to follow him.',
                         'generic_morale_bonus', {'army_morale_factor': 0.10, 'war_support_factor': 0.10, 'political_power_gain': 0.10}),
    'dv_angevin_empire': ('The Angevin Empire', 'From the Scottish border to the Pyrenees, the lands of the Plantagenets hold together.',
                          'generic_fortify_the_borders', {'army_defence_factor': 0.10, 'stability_factor': 0.05}),
    'dv_exchequer': ('The Exchequer', 'Royal clerks count the king\'s revenues on a chequered cloth, and nothing escapes them.',
                     'generic_central_management', {'political_power_gain': 0.15, 'production_speed_buildings_factor': 0.05}),
    'dv_common_law': ('The Common Law', 'Royal justices ride out across the kingdom, and the same law holds everywhere.',
                      'generic_constitutional_guarantees', {'stability_factor': 0.10, 'political_power_factor': 0.05}),
    'dv_baillis': ('Baillis and Seneschals', 'Paid royal officials, not barons, now run the king\'s lands.',
                   'generic_central_management', {'political_power_gain': 0.15, 'stability_factor': 0.05}),
    'dv_french_chivalry': ('Chivalry of France', 'The heavy horse of France is the finest in Christendom.',
                           'generic_army_war_college', {'army_attack_factor': 0.10, 'army_org_factor': 0.05}),
    'dv_university_of_paris': ('University of Paris', 'Masters and students from all over Christendom gather on the left bank of the Seine.',
                               'generic_research_bonus', {'research_speed_factor': 0.05}),
    'dv_champagne_fairs': ('Fairs of Champagne', 'Merchants from Flanders and Italy meet at Troyes and Provins under royal protection.',
                           'generic_foreign_capital', {'production_speed_buildings_factor': 0.10, 'political_power_gain': 0.10}),
    'dv_rex_franciae': ('Rex Franciae', 'No longer King of the Franks, but King of France.',
                        'generic_pp_unity_bonus', {'stability_factor': 0.10, 'war_support_factor': 0.05, 'political_power_factor': 0.10}),
    'dv_teutonic_order': ('The Teutonic Order', 'A field hospital outside Acre has become an order of German knights.',
                          'generic_infantry_bonus', {'army_defence_factor': 0.10, 'army_org_factor': 0.05}),
    'dv_lombard_towns': ('Lombard Towns', 'The rich cities of Lombardy pay the emperor in silver rather than blood.',
                         'generic_foreign_capital', {'production_speed_buildings_factor': 0.10, 'political_power_gain': 0.05}),
    'dv_ostsiedlung': ('Ostsiedlung', 'German settlers clear the forests and found new towns east of the Elbe.',
                       'generic_agrarian_society', {'monthly_population': 0.15, 'production_speed_buildings_factor': 0.05}),
    'dv_hohenstaufen': ('The Hohenstaufen Empire', 'The house of Staufen rules from the North Sea to Sicily.',
                        'generic_pp_unity_bonus', {'stability_factor': 0.10, 'war_support_factor': 0.05, 'army_attack_factor': 0.05}),
    'dv_varangian_guard': ('The Varangian Guard', 'Axe-bearing Englishmen and Norsemen guard the emperor\'s person.',
                           'generic_infantry_bonus', {'army_defence_factor': 0.10, 'army_org_factor': 0.05}),
    'dv_venetian_quarter': ('The Venetian Quarter', 'Venice trades tax-free in the Golden Horn, and her galleys sail for the emperor.',
                            'generic_foreign_capital', {'production_speed_buildings_factor': 0.10, 'political_power_gain': 0.05}),
    'dv_pisan_quarter': ('Pisan and Genoese Quarters', 'Playing the Italians against each other keeps any one of them from growing too strong.',
                         'generic_foreign_capital', {'production_speed_buildings_factor': 0.05, 'stability_factor': 0.05}),
    'dv_roman_restoration': ('Roman Restoration', 'The empire of the Komnenoi rises again.',
                             'generic_army_war_college', {'army_attack_factor': 0.10, 'war_support_factor': 0.05}),
    'dv_pronoia': ('Pronoia Grants', 'Soldiers are granted the revenues of land in return for service.',
                   'generic_manpower_bonus', {'army_org_factor': 0.05, 'monthly_population': 0.05}),
    'dv_basileia': ('Basileia ton Rhomaion', 'The Empire of the Romans is eternal.',
                    'generic_pp_unity_bonus', {'stability_factor': 0.10, 'political_power_factor': 0.10, 'research_speed_factor': 0.03}),
    'dv_norman_kingdom': ('The Norman Kingdom', 'The Hauteville crown stays in Sicily, whatever the Emperor says.',
                          'generic_fortify_the_borders', {'stability_factor': 0.10, 'army_defence_factor': 0.05}),
    'dv_arab_norman': ('The Diwan of Palermo', 'Greek, Arab and Latin clerks run the richest kingdom in the West.',
                       'generic_research_bonus', {'research_speed_factor': 0.05, 'political_power_gain': 0.10}),
    'dv_lombard_league': ('The Lombard League', 'The free cities of the north stand with the Pope against the Emperor.',
                          'generic_fortify_the_borders', {'army_defence_factor': 0.15}),
    'dv_indulgences': ('Indulgences', 'Remission of sin for those who give to the crusade.',
                       'generic_political_support', {'political_power_gain': 0.20}),
    'dv_lateran_reform': ('Lateran Reform', 'A council of the whole Church reforms the clergy and settles doctrine.',
                          'generic_research_bonus', {'stability_factor': 0.10, 'research_speed_factor': 0.03}),
    'dv_vicar_of_christ': ('Vicar of Christ', 'Kings kneel before the throne of Saint Peter.',
                           'generic_pp_unity_bonus', {'political_power_factor': 0.15, 'stability_factor': 0.05}),
    'dv_turkmen_archers': ('Turkmen Horse Archers', 'Nomad horsemen who strike and vanish before the knights can charge.',
                           'generic_army_war_college', {'army_speed_factor': 0.10, 'army_attack_factor': 0.05}),
    'dv_persian_court': ('The Persian Court of Konya', 'Poets, architects and scholars from Persia fill the sultan\'s capital.',
                         'generic_research_bonus', {'research_speed_factor': 0.04, 'political_power_gain': 0.10}),
    'dv_sultanate_of_rum': ('Sultanate of Rum', 'The Turks rule the lands of Rome in Anatolia, and mean to keep them.',
                            'generic_pp_unity_bonus', {'stability_factor': 0.10, 'war_support_factor': 0.05, 'army_defence_factor': 0.05}),
    'dv_mounted_warriors': ('Mounted Warriors', 'Our best fighters go to war on horseback.',
                            'generic_army_war_college', {'army_attack_factor': 0.05, 'army_speed_factor': 0.05}),
    'dv_old_ways': ('The Old Ways', 'We fight for the gods of our fathers, in the forests and hills we know.',
                    'generic_guerilla_warfare', {'army_defence_factor': 0.10}),
    'dv_faithful_realm': ('A Faithful Realm', 'Prince, priests and people share one faith.',
                          'generic_pp_unity_bonus', {'stability_factor': 0.10, 'war_support_factor': 0.05}),
}

s = 'ideas = {\n\tcountry = {\n'
for k, (name, desc, pic, mods) in IDEAS.items():
    m = ''.join(f'\t\t\t\t{a} = {b}\n' for a, b in mods.items())
    s += (f'\t\t{k} = {{\n\t\t\tpicture = {pic}\n\t\t\tallowed = {{ always = no }}\n'
          f'\t\t\tremoval_cost = -1\n\t\t\tmodifier = {{\n{m}\t\t\t}}\n\t\t}}\n')
    loc(k, name)
    loc(f'{k}_desc', desc)
s += '\t}\n}\n'
w('common/ideas/dv_focus_ideas.txt', s)

OPINIONS = {
    'dv_friendship': (30, 'Friendship'),
    'dv_betrayal': (-30, 'Betrayal'),
}
s = 'opinion_modifiers = {\n'
for k, (v, name) in OPINIONS.items():
    s += f'\t{k} = {{\n\t\tvalue = {v}\n\t}}\n'
    loc(k, name)
s += '}\n'
w('common/opinion_modifiers/dv_focus_opinions.txt', s)


# ---------------------------------------------------------------- reusable rewards
def wargoal(target, states, kind='take_state_focus'):
    gen = f' generator = {{ {" ".join(map(str, states))} }}' if states else ''
    return ind(f'''
if = {{
	limit = {{ country_exists = {target} NOT = {{ has_war_with = {target} }} }}
	create_wargoal = {{ type = {kind} target = {target}{gen} }}
}}''')


def claims(states):
    return ''.join(f'{T3}add_state_claim = {s}\n' for s in states)


def opinion(target, mod='dv_friendship', both=True):
    back = f'\n\t{target} = {{ add_opinion_modifier = {{ target = ROOT modifier = {mod} }} }}' if both else ''
    return ind(f'''
if = {{
	limit = {{ country_exists = {target} }}
	add_opinion_modifier = {{ target = {target} modifier = {mod} }}{back}
}}''')


def castle(state, level):
    return ind(f'''
{state} = {{
	add_building_construction = {{
		type = bunker level = {level} instant_build = yes
		province = {{ all_provinces = yes limit_to_victory_point > 0 }}
	}}
}}''')


def offsite(kind, n=1):
    return f'{T3}add_offsite_building = {{ type = {kind} level = {n} }}\n'


def marshal(name, skill, atk, dfn, plan, log):
    return ind(f'''
create_field_marshal = {{
	name = "{name}"
	traits = {{ }}
	skill = {skill}
	attack_skill = {atk}
	defense_skill = {dfn}
	planning_skill = {plan}
	logistics_skill = {log}
}}''')


# Same as the Take the Cross decision, but also works for countries already in the Crusader States faction.
CROSS_AVAILABLE = ind('''
country_exists = JRS
JRS = { has_war_with = AYB }
NOT = { has_war_with = JRS }
OR = {
	is_in_faction = no
	is_in_faction_with = JRS
}''')
CROSS_REWARD = ind('''
if = {
	limit = { is_in_faction = no }
	JRS = { add_to_faction = ROOT }
}
if = {
	limit = { NOT = { has_war_with = AYB } }
	declare_war_on = { target = AYB type = annex_everything }
}
add_ideas = dv_crusader_vow''')
CROSS_DESC = ' We join the Crusader States and go to war with Saladin. If we already swore the vow, this focus completes on its own.'


def take_the_cross(fid, x, y, pre, desc, extra='', name='Take the Cross'):
    return dict(id=fid, name=name, icon='GFX_goal_generic_major_alliance', x=x, y=y, pre=pre, filters=MIL,
                available=CROSS_AVAILABLE, bypass=f'{T3}has_idea = dv_crusader_vow\n',
                desc=desc + CROSS_DESC, reward=CROSS_REWARD + extra, ai=10)


def call_crusade(tags):
    tags = ' '.join(f'tag = {t}' for t in tags)
    return ind(f'''
every_country = {{
	limit = {{
		OR = {{ {tags} }}
		is_ai = yes
		is_in_faction = no
		NOT = {{ has_war_with = JRS }}
		NOT = {{ has_war_with = AYB }}
	}}
	JRS = {{ add_to_faction = PREV }}
	declare_war_on = {{ target = AYB type = annex_everything }}
	add_ideas = dv_crusader_vow
}}''')


# ---------------------------------------------------------------- tree writer
def focus_tree(tree_id, tag, focuses, shared=False):
    if shared:
        # every nation without its own tree gets this one instead of the 1936 generic tree
        country = '\tcountry = {\n\t\tfactor = 5\n\t}\n'
    else:
        country = f'\tcountry = {{\n\t\tfactor = 0\n\t\tmodifier = {{\n\t\t\tadd = 10\n\t\t\ttag = {tag}\n\t\t}}\n\t}}\n'
    s = f'focus_tree = {{\n\tid = {tree_id}\n\n{country}\n\tdefault = no\n\tcontinuous_focus_position = {{ x = 50 y = 1200 }}\n\n'
    ids = {f['id'] for f in focuses}
    for f in focuses:
        s += '\tfocus = {\n'
        s += f"\t\tid = {f['id']}\n\t\ticon = {f['icon']}\n\t\tx = {f['x']}\n\t\ty = {f['y']}\n\t\tcost = {f.get('cost', 5)}\n"
        for p in f.get('pre', []):
            group = p if isinstance(p, tuple) else (p,)
            assert all(g in ids for g in group), (f['id'], p)
            s += '\t\tprerequisite = { ' + ' '.join(f'focus = {g}' for g in group) + ' }\n'
        if f.get('mutex'):
            assert all(m in ids for m in f['mutex']), f['id']
            s += '\t\tmutually_exclusive = { ' + ' '.join(f'focus = {m}' for m in f['mutex']) + ' }\n'
        for block in ['allow_branch', 'available', 'bypass']:
            if f.get(block):
                s += f"\t\t{block} = {{\n{f[block]}\t\t}}\n"
        s += f"\t\tsearch_filters = {{ {' '.join(f.get('filters', ['FOCUS_FILTER_POLITICAL']))} }}\n"
        s += f"\t\tai_will_do = {{\n\t\t\tfactor = {f.get('ai', 1)}\n\t\t}}\n"
        s += f"\t\tcompletion_reward = {{\n{f['reward']}\t\t}}\n"
        s += '\t}\n\n'
        loc(f['id'], f['name'])
        loc(f"{f['id']}_desc", f['desc'])
    return s.rstrip('\n') + '\n}\n'


def g(fid, name, icon, x, y, desc, reward, **kw):
    return dict(id=fid, name=name, icon=f'GFX_goal_generic_{icon}', x=x, y=y, desc=desc, reward=reward, **kw)


# ---------------------------------------------------------------- Angevin England
AGV = [
    g('dv_agv_angevin_inheritance', 'The Angevin Inheritance', 'national_unity', 7, 0, cost=3,
      desc='King Henry rules England, Normandy, Anjou and Aquitaine. Holding it all together is the work of a lifetime.',
      reward=f'{T3}add_political_power = 50\n{T3}add_stability = 0.05\n'),
    # crusade
    g('dv_agv_saladin_tithe', 'The Saladin Tithe', 'trade', 2, 1, pre=['dv_agv_angevin_inheritance'],
      desc='A tenth of every man\'s goods and income, to pay for the war in the East.',
      reward=f'{T3}add_political_power = 50\n{T3}add_equipment_to_stockpile = {{ type = infantry_equipment_0 amount = 500 producer = AGV }}\n'),
    take_the_cross('dv_agv_take_the_cross', 2, 2, ['dv_agv_saladin_tithe'],
                   'Richard, Count of Poitou, was the first prince north of the Alps to take the cross.'),
    g('dv_agv_sail_for_outremer', 'Sail for Outremer', 'amphibious_assault', 1, 3, pre=['dv_agv_take_the_cross'], filters=MIL,
      desc='A great fleet gathers at Dartmouth for the long voyage to the Holy Land.',
      reward=f'{T3}navy_experience = 25\n{T3}add_manpower = 5000\n'),
    g('dv_agv_lionheart', 'The Lionheart', 'position_armies', 3, 3, pre=['dv_agv_take_the_cross'], filters=MIL,
      desc='Richard is the greatest soldier of the age, and he wants to command in person.',
      reward=marshal('Richard the Lionheart', 5, 6, 3, 4, 3)),
    g('dv_agv_conquest_of_cyprus', 'The Conquest of Cyprus', 'occupy_states_coastal', 1, 4, pre=['dv_agv_sail_for_outremer'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = CYK }}\n',
      desc='Isaac Komnenos mistreated our shipwrecked sailors. Cyprus will pay for it, and make a fine base for the crusade.',
      reward=claims([183]) + wargoal('CYK', [183])),
    g('dv_agv_siege_of_acre', 'The Siege of Acre', 'army_artillery', 3, 4, pre=['dv_agv_lionheart'], filters=MIL,
      desc='Bring up the siege towers and the great trebuchets. Acre must fall.',
      reward=f'{T3}army_experience = 25\n{T3}add_equipment_to_stockpile = {{ type = artillery_equipment_1 amount = 100 producer = AGV }}\n'),
    g('dv_agv_crusader_king', 'Return of the Crusader King', 'propaganda', 2, 5, pre=['dv_agv_conquest_of_cyprus', 'dv_agv_siege_of_acre'],
      desc='The king comes home from the Holy Land with his fame spread across Christendom.',
      reward=f'{T3}add_ideas = dv_crusader_king\n'),
    # the Angevin lands
    g('dv_agv_rebellious_sons', 'The Rebellious Sons', 'political_pressure', 7, 1, pre=['dv_agv_angevin_inheritance'],
      desc='Henry\'s sons have risen against him before and will again. Settle the succession before France can use it.',
      reward=f'{T3}add_stability = 0.10\n'),
    g('dv_agv_defend_normandy', 'Defend Normandy', 'defence', 7, 2, pre=['dv_agv_rebellious_sons'], filters=MIL,
      desc='The duchy is the heart of our lands across the sea, and the French king covets it.',
      reward=castle(15, 2) + f'{T3}add_manpower = 5000\n'),
    g('dv_agv_hold_the_empire', 'Hold the Angevin Empire', 'fortify_city', 6, 3, pre=['dv_agv_defend_normandy'],
      mutex=['dv_agv_crush_the_capetians'],
      desc='Keep what we have. Every castle from Rouen to Bordeaux will be ready.',
      reward=f'{T3}add_ideas = dv_angevin_empire\n'),
    g('dv_agv_crush_the_capetians', 'Crush the Capetians', 'major_war', 8, 3, pre=['dv_agv_defend_normandy'], filters=MIL,
      mutex=['dv_agv_hold_the_empire'], ai=0.2,
      desc='The King of France is our vassal for Normandy, yet he plots against us. Take Picardy and the Vexin and end the threat.',
      reward=claims([785, 29]) + wargoal('FRK', [785, 29])),
    g('dv_agv_chateau_gaillard', 'Chateau Gaillard', 'construction', 7, 4, pre=[('dv_agv_hold_the_empire', 'dv_agv_crush_the_capetians')], filters=IND,
      desc='Build the strongest castle in the world on the cliffs above the Seine.',
      reward=castle(15, 2) + offsite('arms_factory')),
    # the British Isles
    g('dv_agv_exchequer', 'The Exchequer', 'production', 12, 1, pre=['dv_agv_angevin_inheritance'], filters=IND,
      desc='Make the royal treasury the best run in Europe.',
      reward=f'{T3}add_ideas = dv_exchequer\n'),
    g('dv_agv_lordship_of_ireland', 'Lordship of Ireland', 'occupy_states_coastal', 10, 2, pre=['dv_agv_exchequer'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = IRK }}\n',
      desc='Prince John is Lord of Ireland, but the Irish kings do not accept it. Finish the conquest Strongbow began.',
      reward=claims([134, 119]) + wargoal('IRK', [134, 119])),
    g('dv_agv_welsh_marches', 'The Welsh Marches', 'territory_or_war', 10, 3, pre=['dv_agv_lordship_of_ireland'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = GWY }}\n',
      desc='The Lord Rhys still raids the marcher lordships. Wales must be brought under the crown.',
      reward=claims([122]) + wargoal('GWY', [122])),
    g('dv_agv_treaty_of_falaise', 'Enforce the Treaty of Falaise', 'military_sphere', 12, 2, pre=['dv_agv_exchequer'],
      mutex=['dv_agv_quitclaim_of_canterbury'], bypass=f'{T3}NOT = {{ country_exists = SCT }}\n', ai=0.3,
      desc='William the Lion swore homage to Henry for all of Scotland. Make him keep that oath.',
      reward=wargoal('SCT', [], 'puppet_wargoal_focus')),
    g('dv_agv_quitclaim_of_canterbury', 'Quitclaim of Canterbury', 'improve_relations', 14, 2, pre=['dv_agv_exchequer'],
      mutex=['dv_agv_treaty_of_falaise'],
      desc='Sell the Scots their freedom for ten thousand marks. We need the silver more than their homage.',
      reward=f'{T3}add_political_power = 100\n' + opinion('SCT')),
    g('dv_agv_wool_trade', 'The Wool Trade', 'consumer_goods', 13, 3, pre=[('dv_agv_treaty_of_falaise', 'dv_agv_quitclaim_of_canterbury')], filters=IND,
      desc='English wool clothes half of Flanders. Tax the trade and build on it.',
      reward=offsite('industrial_complex', 2)),
    g('dv_agv_common_law', 'The Common Law', 'national_unity', 12, 4, pre=['dv_agv_welsh_marches', 'dv_agv_wool_trade'],
      desc='The king\'s justices bring one law to the whole realm.',
      reward=f'{T3}add_ideas = dv_common_law\n'),
]

# ---------------------------------------------------------------- Kingdom of France
FRK = [
    g('dv_frk_philip_augustus', 'Philip Augustus', 'national_unity', 6, 0, cost=3,
      desc='The young king has a weak crown and powerful neighbours. He means to change both.',
      reward=f'{T3}add_political_power = 50\n{T3}add_stability = 0.05\n'),
    # crusade
    take_the_cross('dv_frk_take_the_cross', 2, 1, ['dv_frk_philip_augustus'],
                   'At Gisors the kings of France and England swore to go on crusade together.'),
    g('dv_frk_genoese_fleet', 'Hire the Genoese Fleet', 'build_navy', 1, 2, pre=['dv_frk_take_the_cross'], filters=MIL,
      desc='France has no fleet of her own. Genoa will carry our army to the East, for a price.',
      reward=f'{T3}navy_experience = 20\n{T3}add_manpower = 5000\n'),
    g('dv_frk_siege_of_acre', 'The Siege of Acre', 'army_artillery', 3, 2, pre=['dv_frk_take_the_cross'], filters=MIL,
      desc='Our engineers will bring down the walls of Acre.',
      reward=f'{T3}army_experience = 25\n{T3}add_equipment_to_stockpile = {{ type = artillery_equipment_1 amount = 100 producer = FRK }}\n'),
    g('dv_frk_return_to_france', 'Return to France', 'political_pressure', 1, 3, pre=[('dv_frk_genoese_fleet', 'dv_frk_siege_of_acre')],
      mutex=['dv_frk_stay_the_course'], ai=0.5,
      desc='Acre is enough. While Richard stays in the East, his lands in France lie open. Make peace with Saladin, leave the crusade and go home.',
      reward=ind('''
if = {
	limit = { has_war_with = AYB }
	white_peace = AYB
}
if = {
	limit = { is_in_faction_with = JRS }
	leave_faction = yes
}
remove_ideas = dv_crusader_vow
add_political_power = 100''') + claims([15, 30])),
    g('dv_frk_stay_the_course', 'Stay the Course', 'major_alliance', 3, 3, pre=[('dv_frk_genoese_fleet', 'dv_frk_siege_of_acre')], filters=MIL,
      mutex=['dv_frk_return_to_france'],
      desc='We swore to see Jerusalem. The King of France keeps his oaths.',
      reward=f'{T3}add_ideas = dv_crusader_king\n'),
    # the Angevin rivalry
    g('dv_frk_royal_demesne', 'Expand the Royal Demesne', 'more_territorial_claims', 6, 1, pre=['dv_frk_philip_augustus'],
      desc='The king himself holds little more than Paris and Orleans. Every new fief must come to the crown.',
      reward=f'{T3}add_political_power = 50\n' + offsite('industrial_complex')),
    g('dv_frk_baillis', 'Baillis and Seneschals', 'production', 5, 2, pre=['dv_frk_royal_demesne'],
      desc='Send salaried royal officials to govern the king\'s lands in his name.',
      reward=f'{T3}add_ideas = dv_baillis\n'),
    g('dv_frk_young_princes', 'Court the Young Princes', 'dangerous_deal', 7, 2, pre=['dv_frk_royal_demesne'],
      desc='Henry\'s sons quarrel with their father. Welcome them in Paris and turn them against him.',
      reward=f'{T3}add_political_power = 50\n' + ind('''
if = {
	limit = { country_exists = AGV }
	AGV = { add_stability = -0.05 }
}''')),
    g('dv_frk_claim_normandy', 'Claim Normandy', 'territory_or_war', 7, 3, pre=['dv_frk_young_princes'], filters=MIL,
      desc='The King of England holds Normandy, Anjou and Poitou as our vassal. A vassal who defies his lord forfeits his fiefs.',
      reward=claims([15, 14, 30, 23]) + wargoal('AGV', [15, 30])),
    g('dv_frk_road_to_bouvines', 'The Road to Bouvines', 'army_doctrines', 6, 4, pre=['dv_frk_baillis', 'dv_frk_claim_normandy'], filters=MIL,
      desc='Gather the knights of France for the battle that will decide the fate of the West.',
      reward=f'{T3}add_ideas = dv_french_chivalry\n{T3}army_experience = 25\n'),
    # Paris
    g('dv_frk_walls_of_paris', 'The Walls of Paris', 'fortify_city', 11, 1, pre=['dv_frk_philip_augustus'], filters=IND,
      desc='Before the king leaves for the East, his capital must have walls worthy of it.',
      reward=castle(16, 2) + f'{T3}16 = {{ add_building_construction = {{ type = infrastructure level = 1 instant_build = yes }} }}\n'),
    g('dv_frk_louvre', 'The Louvre', 'construct_military', 10, 2, pre=['dv_frk_walls_of_paris'], filters=IND,
      desc='A great keep on the Seine to guard the city and hold the royal treasure and arsenal.',
      reward=offsite('arms_factory')),
    g('dv_frk_university_of_paris', 'University of Paris', 'scientific_exchange', 12, 2, pre=['dv_frk_walls_of_paris'], filters=RES,
      desc='Grant the masters and students of Paris the protection of the crown.',
      reward=f'{T3}add_ideas = dv_university_of_paris\n'),
    g('dv_frk_champagne_fairs', 'Fairs of Champagne', 'trade', 11, 3, pre=['dv_frk_louvre', 'dv_frk_university_of_paris'], filters=IND,
      desc='Protect the merchants on the roads to Troyes and Provins, and let the silver flow.',
      reward=f'{T3}add_ideas = dv_champagne_fairs\n'),
    g('dv_frk_rex_franciae', 'Rex Franciae', 'political_pressure', 9, 5, pre=['dv_frk_road_to_bouvines', 'dv_frk_champagne_fairs'],
      desc='Our chancery now calls the king King of France. The realm and the crown are one.',
      reward=f'{T3}add_ideas = dv_rex_franciae\n'),
]

# ---------------------------------------------------------------- Holy Roman Empire
HRE = [
    g('dv_hre_diet_of_christ', 'The Diet of Christ', 'national_unity', 6, 0, cost=3,
      desc='At Mainz the emperor has called a diet of all the princes, with Christ himself named as its president.',
      reward=f'{T3}add_political_power = 50\n{T3}add_war_support = 0.05\n'),
    # crusade
    take_the_cross('dv_hre_take_the_cross', 2, 1, ['dv_hre_diet_of_christ'],
                   'Old Barbarossa takes the cross from the hands of the bishop of Wurzburg.',
                   extra=marshal('Frederick Barbarossa', 4, 4, 4, 4, 3)),
    g('dv_hre_passage_through_hungary', 'Passage through Hungary', 'improve_relations', 2, 2, pre=['dv_hre_take_the_cross'],
      desc='King Bela is a friend. Ask him for passage and supplies for the army on its way east.',
      reward=ind('''
if = {
	limit = { country_exists = HNG NOT = { has_war_with = HNG } }
	HNG = { give_military_access = ROOT }
	add_opinion_modifier = { target = HNG modifier = dv_friendship }
	HNG = { add_opinion_modifier = { target = ROOT modifier = dv_friendship } }
}''')),
    g('dv_hre_bargain_with_isaac', 'Bargain with Isaac Angelos', 'positive_trade_relations', 1, 3, pre=['dv_hre_passage_through_hungary'],
      mutex=['dv_hre_force_the_passage'],
      desc='The Greek emperor does not trust us. Hostages and gold may still buy safe passage over the Hellespont.',
      reward=f'{T3}add_political_power = -50\n' + ind('''
if = {
	limit = { country_exists = BYZ NOT = { has_war_with = BYZ } }
	BYZ = { give_military_access = ROOT }
}''')),
    g('dv_hre_force_the_passage', 'Force the Passage', 'occupy_start_war', 3, 3, pre=['dv_hre_passage_through_hungary'], filters=MIL,
      mutex=['dv_hre_bargain_with_isaac'], ai=0.3,
      desc='Isaac has made a pact with Saladin and imprisoned our envoys. Take Philippopolis and Adrianople and make him see sense.',
      reward=f'{T3}army_experience = 10\n' + wargoal('BYZ', [212, 341])),
    g('dv_hre_storm_of_iconium', 'The Storm of Iconium', 'occupy_states_ongoing_war', 2, 4, pre=[('dv_hre_bargain_with_isaac', 'dv_hre_force_the_passage')], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = RUM }}\n',
      desc='The Seljuks of Rum harass our march at every step. Storm their capital and open the road to Syria.',
      reward=f'{T3}army_experience = 25\n' + wargoal('RUM', [346])),
    g('dv_hre_teutonic_order', 'The Teutonic Order', 'special_forces', 2, 5, pre=['dv_hre_storm_of_iconium'], filters=MIL,
      desc='The German hospital at Acre becomes a military order of its own.',
      reward=f'{T3}add_ideas = dv_teutonic_order\n'),
    # Italy
    g('dv_hre_italian_policy', 'The Italian Policy', 'political_pressure', 6, 1, pre=['dv_hre_diet_of_christ'],
      desc='The emperor is King of Italy too. Lombardy, Tuscany and Rome must be brought to order.',
      reward=f'{T3}add_political_power = 50\n'),
    g('dv_hre_peace_of_constance', 'Honour the Peace of Constance', 'improve_relations', 5, 2, pre=['dv_hre_italian_policy'], filters=IND,
      mutex=['dv_hre_pressure_the_pope'],
      desc='Let the Lombard cities govern themselves, and let them pay for the privilege.',
      reward=f'{T3}add_ideas = dv_lombard_towns\n'),
    g('dv_hre_pressure_the_pope', 'Pressure the Pope', 'territory_or_war', 7, 2, pre=['dv_hre_italian_policy'], filters=MIL,
      mutex=['dv_hre_peace_of_constance'], ai=0.2,
      desc='The Pope crowns emperors, but he should not choose them. Bring Rome under imperial authority.',
      reward=claims([2]) + wargoal('PPS', [2])),
    g('dv_hre_sicilian_marriage', 'The Sicilian Marriage', 'more_territorial_claims', 6, 3, pre=[('dv_hre_peace_of_constance', 'dv_hre_pressure_the_pope')],
      desc='Prince Henry has married Constance, heiress of Sicily. When King William dies, the kingdom is ours by right.',
      reward=claims([115, 117, 156, 849, 157, 116])),
    g('dv_hre_crown_of_sicily', 'The Crown of Sicily', 'major_war', 6, 4, pre=['dv_hre_sicilian_marriage'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = SCL }}\n',
      desc='The Sicilian barons have crowned the bastard Tancred. Take what belongs to Constance.',
      reward=wargoal('SCL', [], 'annex_everything')),
    # Germany
    g('dv_hre_imperial_diet', 'The Imperial Diet', 'national_unity', 11, 1, pre=['dv_hre_diet_of_christ'],
      desc='The princes of the Empire must be bound to the emperor by oath and by interest.',
      reward=f'{T3}add_stability = 0.10\n'),
    g('dv_hre_fall_of_the_lion', 'The Fall of Henry the Lion', 'military_sphere', 10, 2, pre=['dv_hre_imperial_diet'],
      desc='Henry the Lion has been stripped of Saxony and Bavaria. Share out his lands among loyal men.',
      reward=f'{T3}add_political_power = 75\n{T3}add_manpower = 10000\n'),
    g('dv_hre_ostsiedlung', 'Ostsiedlung', 'construct_infrastructure', 12, 2, pre=['dv_hre_imperial_diet'], filters=IND,
      desc='Invite settlers from Flanders and the Rhineland to farm the lands east of the Elbe.',
      reward=f'{T3}add_ideas = dv_ostsiedlung\n'),
    g('dv_hre_imperial_cities', 'Free Imperial Cities', 'construct_civ_factory', 11, 3, pre=['dv_hre_fall_of_the_lion', 'dv_hre_ostsiedlung'], filters=IND,
      desc='Grant charters to the towns. They answer to the emperor alone and pay him well.',
      reward=offsite('industrial_complex', 2)),
    g('dv_hre_hohenstaufen', 'The Hohenstaufen Empire', 'political_pressure', 9, 5, pre=['dv_hre_crown_of_sicily', 'dv_hre_imperial_cities'],
      desc='The house of Staufen stands above every other house in Christendom.',
      reward=f'{T3}add_ideas = dv_hohenstaufen\n'),
]

# ---------------------------------------------------------------- Byzantine Empire
BYZ = [
    g('dv_byz_isaac_angelos', 'Isaac Angelos', 'national_unity', 6, 0, cost=3,
      desc='The mob of Constantinople has torn Andronikos apart and made Isaac Angelos emperor. He must now rule.',
      reward=f'{T3}add_political_power = 50\n{T3}add_stability = 0.05\n'),
    # diplomacy
    g('dv_byz_crusader_problem', 'The Crusader Problem', 'political_pressure', 2, 1, pre=['dv_byz_isaac_angelos'],
      desc='Another great Latin army is coming east, and its road runs through our lands.',
      reward=f'{T3}add_political_power = 50\n'),
    g('dv_byz_pact_with_saladin', 'Pact with Saladin', 'neutrality_focus', 1, 2, pre=['dv_byz_crusader_problem'],
      mutex=['dv_byz_aid_the_crusaders'],
      desc='The Latins are a greater danger to us than the Sultan. Make an understanding with Saladin.',
      reward=ind('''
if = {
	limit = { country_exists = AYB NOT = { has_war_with = AYB } }
	diplomatic_relation = { country = AYB relation = non_aggression_pact active = yes }
}''') + opinion('AYB')),
    g('dv_byz_aid_the_crusaders', 'Aid the Crusaders', 'improve_relations', 3, 2, pre=['dv_byz_crusader_problem'],
      mutex=['dv_byz_pact_with_saladin'],
      desc='Open the roads and the markets to the Latin armies, and let them fight the Turks for us.',
      reward=''.join(ind(f'''
if = {{
	limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} }} }}
	give_military_access = {t}
	add_opinion_modifier = {{ target = {t} modifier = dv_friendship }}
	{t} = {{ add_opinion_modifier = {{ target = ROOT modifier = dv_friendship }} }}
}}''') for t in ['HRE', 'FRK', 'AGV'])),
    g('dv_byz_recover_cyprus', 'Recover Cyprus', 'occupy_states_coastal', 2, 3, pre=[('dv_byz_pact_with_saladin', 'dv_byz_aid_the_crusaders')], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = CYK }}\n',
      desc='Isaac Komnenos calls himself emperor in Cyprus. The island and its usurper must be brought back.',
      reward=claims([183]) + wargoal('CYK', [183])),
    g('dv_byz_favour_venice', 'Favour Venice', 'trade', 1, 4, pre=['dv_byz_recover_cyprus'], filters=IND,
      mutex=['dv_byz_favour_pisa'],
      desc='Renew the privileges of the Venetians and let their galleys guard our seas.',
      reward=f'{T3}add_ideas = dv_venetian_quarter\n' + opinion('VNC')),
    g('dv_byz_favour_pisa', 'Favour Pisa and Genoa', 'positive_trade_relations', 3, 4, pre=['dv_byz_recover_cyprus'], filters=IND,
      mutex=['dv_byz_favour_venice'],
      desc='Venice grows too proud. Let Pisa and Genoa share the trade of the City.',
      reward=f'{T3}add_ideas = dv_pisan_quarter\n' + opinion('PSA')),
    # the army
    g('dv_byz_varangian_guard', 'The Varangian Guard', 'special_forces', 6, 1, pre=['dv_byz_isaac_angelos'], filters=MIL,
      desc='Recruit more Englishmen and Norsemen for the emperor\'s own guard.',
      reward=f'{T3}add_ideas = dv_varangian_guard\n'),
    g('dv_byz_vlach_rebellion', 'Crush the Vlach Rebellion', 'major_war', 5, 2, pre=['dv_byz_varangian_guard'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = BLG }}\n',
      desc='Peter and Asen have raised the Bulgarians and Vlachs in revolt and crowned themselves. Put the rebellion down.',
      reward=claims([801, 211, 77, 971]) + wargoal('BLG', [], 'annex_everything')),
    g('dv_byz_greek_fire', 'Greek Fire', 'build_navy', 7, 2, pre=['dv_byz_varangian_guard'], filters=MIL,
      desc='Rebuild the imperial fleet and its secret weapon.',
      reward=f'{T3}navy_experience = 25\n' + offsite('dockyard')),
    g('dv_byz_serbia', 'Bring Serbia to Heel', 'military_sphere', 5, 3, pre=['dv_byz_vlach_rebellion'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = SRB }}\n',
      desc='Stefan Nemanja has thrown off his allegiance. Remind him who his overlord is.',
      reward=wargoal('SRB', [], 'puppet_wargoal_focus')),
    g('dv_byz_reconquer_anatolia', 'Reconquer Anatolia', 'occupy_states_ongoing_war', 7, 3, pre=['dv_byz_greek_fire'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = RUM }}\n',
      desc='Myriokephalon must be avenged. Phrygia and Galatia were Roman for a thousand years.',
      reward=claims([343, 49]) + wargoal('RUM', [343, 49])),
    g('dv_byz_restoration', 'Komnenian Restoration', 'army_doctrines', 6, 4, pre=['dv_byz_serbia', 'dv_byz_reconquer_anatolia'], filters=MIL,
      desc='The army of Manuel Komnenos is reborn.',
      reward=f'{T3}add_ideas = dv_roman_restoration\n{T3}army_experience = 25\n'),
    # the state
    g('dv_byz_pronoia', 'Pronoia Grants', 'allies_build_infantry', 11, 1, pre=['dv_byz_isaac_angelos'],
      desc='Grant soldiers the revenues of land in return for service in the field.',
      reward=f'{T3}add_ideas = dv_pronoia\n'),
    g('dv_byz_theodosian_walls', 'The Theodosian Walls', 'fortify_city', 10, 2, pre=['dv_byz_pronoia'], filters=IND,
      desc='No enemy has ever taken the City by storm. Repair the walls and keep it so.',
      reward=castle(797, 3)),
    g('dv_byz_hagia_sophia', 'Hagia Sophia', 'propaganda', 12, 2, pre=['dv_byz_pronoia'],
      desc='The emperor gives rich gifts to the Great Church, and the Patriarch blesses his reign.',
      reward=f'{T3}add_stability = 0.10\n{T3}add_political_power = 50\n'),
    g('dv_byz_basileia', 'Basileia ton Rhomaion', 'political_pressure', 11, 3, pre=['dv_byz_theodosian_walls', 'dv_byz_hagia_sophia'],
      desc='The Empire of the Romans has outlived every enemy. It will outlive these too.',
      reward=f'{T3}add_ideas = dv_basileia\n'),
]
# ---------------------------------------------------------------- Kingdom of Sicily
SCL = [
    g('dv_scl_william_the_good', 'William the Good', 'national_unity', 5, 0, cost=3,
      desc='The young king of Sicily is rich, pious and childless. His kingdom is the envy of the Mediterranean.',
      reward=f'{T3}add_political_power = 50\n'),
    g('dv_scl_margaritus', 'Margaritus of Brindisi', 'build_navy', 2, 1, pre=['dv_scl_william_the_good'], filters=MIL,
      desc='The great admiral is ready to sail for the Levant with sixty galleys.',
      reward=f'{T3}navy_experience = 25\n'),
    take_the_cross('dv_scl_take_the_cross', 2, 2, ['dv_scl_margaritus'],
                   'King William puts on sackcloth for the loss of Jerusalem and swears to send help.'),
    g('dv_scl_relieve_tripoli', 'Relieve Tripoli', 'amphibious_assault', 2, 3, pre=['dv_scl_take_the_cross'], filters=MIL,
      desc='Our fleet can keep Tripoli and Tyre supplied while the kings of the North gather their armies.',
      reward=f'{T3}army_experience = 15\n' + ind('''
if = {
	limit = { country_exists = TRP }
	TRP = { add_manpower = 3000 }
}''') + opinion('TRP')),
    g('dv_scl_hauteville_succession', 'The Hauteville Succession', 'political_pressure', 5, 1, pre=['dv_scl_william_the_good'],
      desc='William has no son. His aunt Constance is married to the Emperor\'s heir. Who will wear the crown?',
      reward=f'{T3}add_political_power = 50\n'),
    g('dv_scl_crown_tancred', 'Crown Tancred of Lecce', 'fortify_city', 4, 2, pre=['dv_scl_hauteville_succession'],
      mutex=['dv_scl_accept_constance'],
      desc='Better a Norman bastard than a German emperor. The barons crown Tancred.',
      reward=f'{T3}add_ideas = dv_norman_kingdom\n' + opinion('HRE', 'dv_betrayal')),
    g('dv_scl_accept_constance', 'Accept Constance and Henry', 'improve_relations', 6, 2, pre=['dv_scl_hauteville_succession'],
      mutex=['dv_scl_crown_tancred'], ai=0,
      desc='Honour the oath sworn to Constance. Sicily becomes part of the Emperor\'s realm.',
      reward=ind('''
if = {
	limit = { country_exists = HRE NOT = { has_war_with = HRE } }
	HRE = { puppet = ROOT }
}''')),
    g('dv_scl_diwan', 'The Diwan of Palermo', 'scientific_exchange', 5, 3, pre=[('dv_scl_crown_tancred', 'dv_scl_accept_constance')], filters=RES,
      desc='Greek, Arab and Latin clerks keep the finest records and fullest treasury in the West.',
      reward=f'{T3}add_ideas = dv_arab_norman\n'),
    g('dv_scl_eastern_ambitions', 'Eastern Ambitions', 'more_territorial_claims', 9, 1, pre=['dv_scl_william_the_good'],
      desc='Robert Guiscard nearly took Constantinople. The Greek empire is weak again.',
      reward=claims([44, 731, 805])),
    g('dv_scl_march_on_thessalonica', 'March on Thessalonica', 'major_war', 8, 2, pre=['dv_scl_eastern_ambitions'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = BYZ }}\n', ai=0.3,
      desc='Two years ago our army sacked Thessalonica. This time we keep it.',
      reward=wargoal('BYZ', [44, 731])),
    g('dv_scl_harbours_of_apulia', 'Harbours of Apulia', 'construct_naval_dockyard', 10, 2, pre=['dv_scl_eastern_ambitions'], filters=IND,
      desc='Brindisi, Bari and Otranto are the gateways to the East. Enlarge them.',
      reward=offsite('dockyard') + offsite('industrial_complex')),
]

# ---------------------------------------------------------------- Papal States
PPS = [
    g('dv_pps_audita_tremendi', 'Audita Tremendi', 'propaganda', 4, 0, cost=3,
      desc='On hearing with what severe and terrible judgement the land of Jerusalem has been struck... With these words the Pope calls Christendom to arms.',
      reward=f'{T3}add_political_power = 75\n' + ind('''
every_country = {
	limit = { has_idea = dv_catholic }
	add_war_support = 0.05
}''')),
    g('dv_pps_preach_the_crusade', 'Preach the Crusade', 'major_alliance', 2, 1, pre=['dv_pps_audita_tremendi'],
      available=f'{T3}country_exists = JRS\n{T3}JRS = {{ has_war_with = AYB }}\n',
      desc='Send legates to every Catholic court. England, France, the Empire, Sicily and Hungary join the Crusader States if the AI rules them.',
      reward=call_crusade(['AGV', 'FRK', 'HRE', 'SCL', 'HNG'])),
    g('dv_pps_military_orders', 'Bless the Military Orders', 'special_forces', 2, 2, pre=['dv_pps_preach_the_crusade'],
      desc='Confirm the privileges of the Templars and Hospitallers, who answer only to the Pope.',
      reward=f'{T3}add_political_power = 50\n' + ind('''
if = {
	limit = { country_exists = JRS NOT = { JRS = { has_idea = dv_military_orders } } }
	JRS = { add_ideas = dv_military_orders }
}''')),
    g('dv_pps_indulgences', 'Indulgences', 'trade', 2, 3, pre=['dv_pps_military_orders'],
      desc='Those who cannot go on crusade may still give to it, and win remission of their sins.',
      reward=f'{T3}add_ideas = dv_indulgences\n'),
    g('dv_pps_reconcile_with_the_emperor', 'Reconcile with the Emperor', 'improve_relations', 5, 1, pre=['dv_pps_audita_tremendi'],
      mutex=['dv_pps_lombard_league'],
      desc='The crusade needs Barbarossa. Make peace with him and crown his son.',
      reward=f'{T3}add_stability = 0.05\n' + opinion('HRE')),
    g('dv_pps_lombard_league', 'Back the Lombard League', 'fortify_city', 7, 1, pre=['dv_pps_audita_tremendi'],
      mutex=['dv_pps_reconcile_with_the_emperor'],
      desc='The Emperor wants Sicily and Rome both. Stand with the free cities of the north against him.',
      reward=f'{T3}add_ideas = dv_lombard_league\n' + opinion('HRE', 'dv_betrayal')),
    g('dv_pps_patrimony', 'Patrimony of Saint Peter', 'more_territorial_claims', 6, 2, pre=[('dv_pps_reconcile_with_the_emperor', 'dv_pps_lombard_league')],
      desc='The lands of the Church stretch from Rome to Ravenna, whatever the Emperor\'s men say.',
      reward=claims([161]) + offsite('industrial_complex')),
    g('dv_pps_lateran_council', 'Lateran Council', 'scientific_exchange', 6, 3, pre=['dv_pps_patrimony'], filters=RES,
      desc='Call the bishops of all Christendom to Rome to reform the Church.',
      reward=f'{T3}add_ideas = dv_lateran_reform\n'),
    g('dv_pps_vicar_of_christ', 'Vicar of Christ', 'political_pressure', 4, 4, pre=['dv_pps_indulgences', 'dv_pps_lateran_council'],
      desc='The Pope is no longer only the Vicar of Peter, but the Vicar of Christ, set above kings.',
      reward=f'{T3}add_ideas = dv_vicar_of_christ\n'),
]

# ---------------------------------------------------------------- Sultanate of Rum
RUM = [
    g('dv_rum_kilij_arslan', 'Kilij Arslan\'s Legacy', 'national_unity', 5, 0, cost=3,
      desc='The old sultan has divided his lands among his eleven sons. The sultanate must survive his generosity.',
      reward=f'{T3}add_political_power = 50\n'),
    g('dv_rum_turkmen', 'Turkmen Horse Archers', 'cavalry', 2, 1, pre=['dv_rum_kilij_arslan'], filters=MIL,
      desc='Call the Turkmen tribes of the uplands to the sultan\'s banner.',
      reward=f'{T3}add_ideas = dv_turkmen_archers\n'),
    g('dv_rum_defend_iconium', 'Defend Iconium', 'defence', 2, 2, pre=['dv_rum_turkmen'], filters=MIL,
      desc='Barbarossa\'s army is on the march. Konya must not fall.',
      reward=castle(346, 2) + f'{T3}add_manpower = 5000\n'),
    g('dv_rum_harry_the_franks', 'Harry the Franks', 'position_armies', 2, 3, pre=['dv_rum_defend_iconium'], filters=MIL,
      desc='Burn the fields, poison the wells and pick off stragglers. Let hunger and heat fight for us.',
      reward=f'{T3}army_experience = 20\n{T3}add_war_support = 0.05\n'),
    g('dv_rum_reunite_the_sons', 'Reunite the Sons', 'political_pressure', 5, 1, pre=['dv_rum_kilij_arslan'],
      desc='One sultan, one army, one treasury.',
      reward=f'{T3}add_stability = 0.15\n'),
    g('dv_rum_caravanserais', 'Caravanserais', 'construct_infrastructure', 5, 2, pre=['dv_rum_reunite_the_sons'], filters=IND,
      desc='Build fortified inns a day\'s ride apart on the trade roads.',
      reward=f'{T3}346 = {{ add_building_construction = {{ type = infrastructure level = 1 instant_build = yes }} }}\n' + offsite('industrial_complex')),
    g('dv_rum_persian_court', 'The Persian Court', 'scientific_exchange', 5, 3, pre=['dv_rum_caravanserais'], filters=RES,
      desc='Make Konya a city of poets, scholars and builders.',
      reward=f'{T3}add_ideas = dv_persian_court\n'),
    g('dv_rum_byzantine_frontier', 'The Byzantine Frontier', 'more_territorial_claims', 8, 1, pre=['dv_rum_kilij_arslan'],
      desc='The Greeks are weak and divided. The frontier can move west again.',
      reward=f'{T3}add_political_power = 50\n'),
    g('dv_rum_myriokephalon', 'Spirit of Myriokephalon', 'army_doctrines', 8, 2, pre=['dv_rum_byzantine_frontier'], filters=MIL,
      desc='We destroyed the army of Emperor Manuel in the mountain passes. We can do it again.',
      reward=f'{T3}army_experience = 15\n'),
    g('dv_rum_push_to_the_sea', 'Push to the Sea', 'occupy_states_coastal', 7, 3, pre=['dv_rum_myriokephalon'], filters=MIL,
      bypass=f'{T3}NOT = {{ country_exists = BYZ }}\n', ai=0.5,
      desc='Antalya and Smyrna would give the sultanate ports on the sea.',
      reward=claims([342, 339]) + wargoal('BYZ', [342, 339])),
    g('dv_rum_embassy_to_saladin', 'Embassy to Saladin', 'improve_relations', 9, 3, pre=['dv_rum_myriokephalon'],
      desc='Saladin is the champion of Islam now. Make sure his armies and ours never meet.',
      reward=ind('''
if = {
	limit = { country_exists = AYB NOT = { has_war_with = AYB } }
	diplomatic_relation = { country = AYB relation = non_aggression_pact active = yes }
}''') + opinion('AYB')),
    g('dv_rum_sultanate_of_rum', 'Sultanate of Rum', 'political_pressure', 5, 4, pre=['dv_rum_persian_court', ('dv_rum_push_to_the_sea', 'dv_rum_embassy_to_saladin')],
      desc='The Turks of Rum are here to stay.',
      reward=f'{T3}add_ideas = dv_sultanate_of_rum\n'),
]

# ---------------------------------------------------------------- shared medieval tree
def faith(*rels):
    return f"{T3}OR = {{ {' '.join(f'has_idea = dv_{r}' for r in rels)} }}\n"


GENERIC = [
    g('dv_gen_consolidate', 'Consolidate the Realm', 'national_unity', 7, 0, cost=3,
      desc='Bring the great lords of the realm to court and make them swear loyalty again.',
      reward=f'{T3}add_political_power = 50\n{T3}add_stability = 0.05\n'),
    # army
    g('dv_gen_levies', 'Call the Levies', 'allies_build_infantry', 2, 1, pre=['dv_gen_consolidate'], filters=MIL,
      desc='Every lord must bring his men when the ruler calls.',
      reward=f'{T3}add_manpower = 3000\n'),
    g('dv_gen_horsemen', 'Mounted Warriors', 'cavalry', 1, 2, pre=['dv_gen_levies'], filters=MIL,
      desc='Train our best fighters to fight from the saddle.',
      reward=f'{T3}add_ideas = dv_mounted_warriors\n'),
    g('dv_gen_archers', 'Drill the Archers', 'small_arms', 3, 2, pre=['dv_gen_levies'], filters=MIL,
      desc='Every village must send bowmen to practise at the butts.',
      reward=f'{T3}add_equipment_to_stockpile = {{ type = infantry_equipment_0 amount = 300 producer = ROOT }}\n{T3}army_experience = 10\n'),
    g('dv_gen_siege_engines', 'Siege Engines', 'army_artillery', 2, 3, pre=['dv_gen_horsemen', 'dv_gen_archers'], filters=MIL,
      desc='Hire engineers who can build mangonels and trebuchets.',
      reward=f'{T3}add_equipment_to_stockpile = {{ type = artillery_equipment_1 amount = 50 producer = ROOT }}\n{T3}army_experience = 10\n'),
    # economy
    g('dv_gen_market_charters', 'Market Charters', 'trade', 6, 1, pre=['dv_gen_consolidate'], filters=IND,
      desc='Grant towns the right to hold markets, and take a share of every sale.',
      reward=offsite('industrial_complex')),
    g('dv_gen_roads', 'Mend the Roads', 'construct_infrastructure', 5, 2, pre=['dv_gen_market_charters'], filters=IND,
      desc='Repair the old roads and bridges so that merchants and armies can move.',
      reward=f'{T3}capital_scope = {{ add_building_construction = {{ type = infrastructure level = 1 instant_build = yes }} }}\n'),
    g('dv_gen_armouries', 'Royal Armouries', 'construct_mil_factory', 7, 2, pre=['dv_gen_market_charters'], filters=IND,
      desc='Bring smiths and armourers to the capital to forge weapons for the host.',
      reward=offsite('arms_factory')),
    g('dv_gen_castles', 'Stone Castles', 'fortify_city', 6, 3, pre=['dv_gen_roads', 'dv_gen_armouries'], filters=IND,
      desc='Replace the old wooden forts with walls of stone.',
      reward=ind('''
capital_scope = {
	add_building_construction = {
		type = bunker level = 2 instant_build = yes
		province = { all_provinces = yes limit_to_victory_point > 0 }
	}
}''')),
    # faith: each nation only sees the branch for its own religion
    g('dv_gen_pilgrims', 'Pilgrims to the Holy Land', 'improve_relations', 9, 1, pre=['dv_gen_consolidate'],
      allow_branch=faith('catholic'),
      desc='Our pilgrims bring back terrible news from Jerusalem. The Pope calls every Catholic ruler to help.',
      reward=f'{T3}add_political_power = 50\n{T3}add_war_support = 0.05\n'),
    take_the_cross('dv_gen_take_the_cross', 9, 2, ['dv_gen_pilgrims'], 'Our lords swear the crusader vow.'),
    g('dv_gen_call_from_cairo', 'The Call from Cairo', 'improve_relations', 11, 1, pre=['dv_gen_consolidate'],
      allow_branch=faith('sunni', 'shia'),
      desc='Saladin asks every Muslim ruler to help him finish the Franks.',
      reward=f'{T3}add_political_power = 50\n{T3}add_war_support = 0.05\n'),
    g('dv_gen_answer_the_jihad', 'Answer the Jihad', 'major_alliance', 11, 2, pre=['dv_gen_call_from_cairo'], filters=MIL,
      available=ind('''
country_exists = AYB
AYB = { has_war_with = JRS }
NOT = { has_war_with = AYB }
OR = {
	is_in_faction = no
	is_in_faction_with = AYB
}'''), bypass=f'{T3}has_idea = dv_jihad\n',
      desc='We join the Ayyubid Alliance and go to war with the Franks. If we already answered the call, this focus completes on its own.',
      reward=ind('''
if = {
	limit = { is_in_faction = no }
	AYB = { add_to_faction = ROOT }
}
if = {
	limit = { NOT = { has_war_with = JRS } }
	declare_war_on = { target = JRS type = annex_everything }
}
add_ideas = dv_jihad''')),
    g('dv_gen_defenders_of_orthodoxy', 'Defenders of Orthodoxy', 'defence', 13, 1, pre=['dv_gen_consolidate'],
      allow_branch=faith('orthodox'),
      desc='Latins to the west, Turks to the south, pagans to the north. The true faith needs defenders.',
      reward=f'{T3}add_stability = 0.05\n{T3}army_experience = 10\n'),
    g('dv_gen_envoys_to_the_patriarch', 'Envoys to the Patriarch', 'improve_relations', 13, 2, pre=['dv_gen_defenders_of_orthodoxy'],
      desc='Send gifts to Constantinople and ask for the blessing of the Patriarch.',
      reward=f'{T3}add_political_power = 75\n' + opinion('BYZ')),
    g('dv_gen_old_ways', 'The Old Ways', 'defence', 15, 1, pre=['dv_gen_consolidate'],
      allow_branch=faith('pagan', 'tengri', 'dharmic', 'native'),
      desc='We keep the faith of our ancestors, whatever the priests of distant lands say.',
      reward=f'{T3}add_ideas = dv_old_ways\n'),
    g('dv_gen_missionaries', 'Receive the Missionaries', 'scientific_exchange', 15, 2, pre=['dv_gen_old_ways'],
      allow_branch=faith('pagan', 'tengri'),
      desc='Hear what the missionaries from Rome, Constantinople and Baghdad have to say. Their friendship brings influence we can spend on converting, if we choose.',
      reward=f'{T3}add_political_power = 100\n'),
    g('dv_gen_faithful_realm', 'A Faithful Realm', 'propaganda', 12, 3,
      pre=[('dv_gen_take_the_cross', 'dv_gen_answer_the_jihad', 'dv_gen_envoys_to_the_patriarch', 'dv_gen_old_ways')],
      desc='Ruler, priests and people stand together in one faith.',
      reward=f'{T3}add_ideas = dv_faithful_realm\n'),
]

TREES = [
    ('dv_angevin_focus', 'AGV', AGV, 'dv_angevin'),
    ('dv_france_focus', 'FRK', FRK, 'dv_france'),
    ('dv_hre_focus', 'HRE', HRE, 'dv_hre'),
    ('dv_byzantine_focus', 'BYZ', BYZ, 'dv_byzantine'),
    ('dv_sicily_focus', 'SCL', SCL, 'dv_sicily'),
    ('dv_papal_focus', 'PPS', PPS, 'dv_papal'),
    ('dv_rum_focus', 'RUM', RUM, 'dv_rum'),
]
for tree_id, tag, focuses, fname in TREES:
    w(f'common/national_focus/{fname}.txt', focus_tree(tree_id, tag, focuses))
w('common/national_focus/dv_medieval_generic.txt', focus_tree('dv_medieval_focus', None, GENERIC, shared=True))

w('localisation/english/dv_focus_l_english.yml', 'l_english:\n' + '\n'.join(LOC) + '\n', bom=True)
print('wrote', len(LOC), 'localisation keys')
