# Writes the religion system, holy war decisions and the Jerusalem and Ayyubid focus trees.
# Usage: python3 gen_content.py <mod folder>
import os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
LOC = []


def w(path, text, bom=False):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='\n').write(text)


def loc(key, text):
    LOC.append(f' {key}:0 "{text}"')


# ---------------------------------------------------------------- religions
# key: (name, description, modifiers)
RELIGIONS = {
    'catholic': ('Catholic', 'The Pope in Rome is the head of the Church, and the call to crusade comes from him.',
                 {'stability_factor': 0.05, 'war_support_factor': 0.05}),
    'orthodox': ('Orthodox', 'The Patriarch of Constantinople guides the faithful of the East.',
                 {'stability_factor': 0.05, 'political_power_factor': 0.10}),
    'sunni': ('Sunni Islam', 'The Abbasid Caliph in Baghdad is the nominal head of the faithful.',
              {'war_support_factor': 0.05, 'army_morale_factor': 0.05}),
    'shia': ('Shia Islam', 'The followers of Ali, a minority among the Muslims of the region.',
             {'stability_factor': 0.05, 'research_speed_factor': 0.03}),
    'pagan': ('Old Gods', 'The old gods of forest and field are still worshipped here, far from any church.',
              {'army_defence_factor': 0.10, 'stability_factor': -0.05}),
    'tengri': ('Tengrism', 'The Eternal Blue Sky rules over the riders of the steppe.',
               {'army_speed_factor': 0.10, 'stability_factor': -0.05}),
    'dharmic': ('Eastern Faiths', 'Buddhist, Hindu and Confucian traditions shape this realm.',
                {'research_speed_factor': 0.05}),
    'native': ('Native Faiths', 'Local traditions, far from the Holy Land.',
               {'army_defence_factor': 0.05}),
}
CHRISTIAN = ['catholic', 'orthodox']
MUSLIM = ['sunni', 'shia']

# ideas granted by decisions and focuses: key: (name, description, picture, modifiers)
IDEAS = {
    'dv_crusader_vow': ('Crusader Vow', 'Our lords have taken the cross. Their sins are forgiven if they fight for Jerusalem.',
                        'generic_morale_bonus', {'army_morale_factor': 0.10, 'war_support_factor': 0.10}),
    'dv_jihad': ('Jihad', 'Our warriors have answered the call to drive the Franks from the lands of Islam.',
                 'generic_morale_bonus', {'army_morale_factor': 0.10, 'war_support_factor': 0.10}),
    'dv_military_orders': ('The Military Orders', 'The Templars and Hospitallers hold the castles of the kingdom and fight to the last man.',
                           'generic_infantry_bonus', {'army_defence_factor': 0.15, 'army_org_factor': 0.05}),
    'dv_turcopoles': ('Turcopoles', 'Locally raised light horsemen who fight in the eastern style.',
                      'generic_army_war_college', {'army_speed_factor': 0.05, 'army_attack_factor': 0.05}),
    'dv_italian_merchants': ('Italian Merchants', 'Genoese, Pisan and Venetian traders keep the ports of the kingdom alive.',
                             'generic_foreign_capital', {'production_speed_buildings_factor': 0.10, 'political_power_gain': 0.10}),
    'dv_kingdom_endures': ('The Kingdom Endures', 'Against every expectation, the Latin Kingdom still stands.',
                           'generic_pp_unity_bonus', {'stability_factor': 0.10, 'war_support_factor': 0.10, 'army_defence_factor': 0.05}),
    'dv_mamluk_regiments': ('Mamluk Regiments', 'Slave-soldiers raised from boyhood to fight, loyal to the sultan alone.',
                            'generic_army_war_college', {'army_attack_factor': 0.10, 'army_org_factor': 0.05}),
    'dv_egyptian_grain': ('Egyptian Grain', 'The Nile harvest feeds the armies of the sultan.',
                          'generic_agrarian_society', {'monthly_population': 0.10, 'stability_factor': 0.05}),
    'dv_madrasas': ('Madrasas and Waqf', 'Religious schools and endowments spread learning and loyalty.',
                    'generic_research_bonus', {'research_speed_factor': 0.05, 'political_power_gain': 0.10}),
    'dv_sultan_of_egypt_and_syria': ('Sultan of Egypt and Syria', 'Saladin rules from the Nile to the Euphrates.',
                                     'generic_pp_unity_bonus', {'stability_factor': 0.10, 'war_support_factor': 0.10, 'army_attack_factor': 0.05}),
}


def idea_block(key, picture, mods, allowed='always = no'):
    m = ''.join(f'\t\t\t\t{k} = {v}\n' for k, v in mods.items())
    return (f'\t\t{key} = {{\n\t\t\tpicture = {picture}\n\t\t\tallowed = {{ {allowed} }}\n'
            f'\t\t\tremoval_cost = -1\n\t\t\tmodifier = {{\n{m}\t\t\t}}\n\t\t}}\n')


s = 'ideas = {\n\tcountry = {\n'
for k, (name, desc, mods) in RELIGIONS.items():
    s += idea_block(f'dv_{k}', 'generic_morale_bonus', mods)
    loc(f'dv_{k}', name)
    loc(f'dv_{k}_desc', desc)
s += '\t}\n}\n'
w('common/ideas/dv_religions.txt', s)

s = 'ideas = {\n\tcountry = {\n'
for k, (name, desc, pic, mods) in IDEAS.items():
    s += idea_block(k, pic, mods)
    loc(k, name)
    loc(f'{k}_desc', desc)
s += '\t}\n}\n'
w('common/ideas/dv_holy_war_ideas.txt', s)

# ---------------------------------------------------------------- opinions between faiths
OPINIONS = {
    'dv_same_faith': (25, 'Shares our faith'),
    'dv_schismatic': (-15, 'Schismatic'),
    'dv_infidel': (-40, 'Infidel'),
}
s = 'opinion_modifiers = {\n'
for k, (v, name) in OPINIONS.items():
    s += f'\t{k} = {{\n\t\tvalue = {v}\n\t}}\n'
    loc(k, name)
s += '}\n'
w('common/opinion_modifiers/dv_faith_opinions.txt', s)


def relation(a, b):
    if a == b:
        return 'dv_same_faith'
    if {a, b} <= set(CHRISTIAN) or {a, b} <= set(MUSLIM):
        return 'dv_schismatic'
    if (a in CHRISTIAN and b in MUSLIM) or (a in MUSLIM and b in CHRISTIAN):
        return 'dv_infidel'
    return None


eff = ''
for a in RELIGIONS:
    inner = ''
    for b in RELIGIONS:
        mod = relation(a, b)
        if mod:
            inner += (f'\t\t\t\tevery_other_country = {{\n\t\t\t\t\tlimit = {{ has_idea = dv_{b} }}\n'
                      f'\t\t\t\t\tadd_opinion_modifier = {{ target = PREV modifier = {mod} }}\n\t\t\t\t}}\n')
    if inner:
        eff += f'\t\t\tevery_country = {{\n\t\t\t\tlimit = {{ has_idea = dv_{a} }}\n{inner}\t\t\t}}\n'
w('common/on_actions/dv_on_actions.txt',
  'on_actions = {\n\ton_startup = {\n\t\teffect = {\n' + eff + '\t\t}\n\t}\n}\n')

# ---------------------------------------------------------------- decisions
w('common/decisions/categories/dv_categories.txt', '''dv_holy_war = {
	icon = generic_crisis
	picture = GFX_decision_cat_generic_hre
	visible = {
		OR = {
			has_idea = dv_catholic
			has_idea = dv_sunni
			has_idea = dv_shia
		}
	}
}

dv_faith = {
	icon = generic_political_actions
	visible = {
		OR = {
			has_idea = dv_pagan
			has_idea = dv_tengri
		}
	}
}
''')
loc('dv_holy_war', 'Holy War')
loc('dv_holy_war_desc', 'Jerusalem is under attack. The faithful on both sides are called to war.')
loc('dv_faith', 'Faith')
loc('dv_faith_desc', 'Missionaries from Rome, Constantinople and Baghdad are at our gates.')

s = '''dv_holy_war = {
	dv_take_the_cross = {
		icon = generic_decision
		cost = 50
		visible = {
			has_idea = dv_catholic
			NOT = { tag = JRS }
			country_exists = JRS
		}
		available = {
			JRS = { has_war_with = AYB }
			is_in_faction = no
			NOT = { has_war_with = JRS }
			NOT = { has_war_with = AYB }
		}
		complete_effect = {
			JRS = { add_to_faction = ROOT }
			declare_war_on = { target = AYB type = annex_everything }
			add_ideas = dv_crusader_vow
		}
		ai_will_do = {
			factor = 1
		}
	}

	dv_answer_the_jihad = {
		icon = generic_decision
		cost = 50
		visible = {
			OR = {
				has_idea = dv_sunni
				has_idea = dv_shia
			}
			NOT = { tag = AYB }
			country_exists = AYB
		}
		available = {
			AYB = { has_war_with = JRS }
			is_in_faction = no
			NOT = { has_war_with = AYB }
			NOT = { has_war_with = JRS }
		}
		complete_effect = {
			AYB = { add_to_faction = ROOT }
			declare_war_on = { target = JRS type = annex_everything }
			add_ideas = dv_jihad
		}
		ai_will_do = {
			factor = 1
		}
	}
}

dv_faith = {
'''
loc('dv_take_the_cross', 'Take the Cross')
loc('dv_take_the_cross_desc', 'Swear the crusader vow, join the Crusader States and march against Saladin.')
loc('dv_answer_the_jihad', 'Answer the Jihad')
loc('dv_answer_the_jihad_desc', 'Join the Ayyubid Alliance and help drive the Franks into the sea.')
for old in ['pagan', 'tengri']:
    for new in ['catholic', 'orthodox', 'sunni']:
        key = f'dv_convert_{old}_to_{new}'
        s += f'''	{key} = {{
		icon = generic_decision
		cost = 100
		visible = {{
			has_idea = dv_{old}
		}}
		complete_effect = {{
			remove_ideas = dv_{old}
			add_ideas = dv_{new}
			add_stability = -0.10
		}}
		ai_will_do = {{
			factor = 0
		}}
	}}

'''
        loc(key, f'Convert to {RELIGIONS[new][0]}')
        loc(f'{key}_desc', f'Abandon the {RELIGIONS[old][0]} and accept {RELIGIONS[new][0]}. The change will unsettle our people for a time.')
s = s.rstrip('\n') + '\n}\n'
w('common/decisions/dv_holy_war.txt', s)


# ---------------------------------------------------------------- focus trees
def focus_tree(tree_id, tag, focuses):
    s = f'''focus_tree = {{
	id = {tree_id}

	country = {{
		factor = 0
		modifier = {{
			add = 10
			tag = {tag}
		}}
	}}

	default = no
	continuous_focus_position = {{ x = 50 y = 1200 }}

'''
    for f in focuses:
        s += '\tfocus = {\n'
        s += f"\t\tid = {f['id']}\n\t\ticon = {f['icon']}\n\t\tx = {f['x']}\n\t\ty = {f['y']}\n\t\tcost = {f.get('cost', 5)}\n"
        for p in f.get('pre', []):
            s += f'\t\tprerequisite = {{ focus = {p} }}\n'
        if f.get('mutex'):
            s += '\t\tmutually_exclusive = { ' + ' '.join(f'focus = {m}' for m in f['mutex']) + ' }\n'
        if f.get('available'):
            s += f"\t\tavailable = {{\n{f['available']}\t\t}}\n"
        s += f"\t\tsearch_filters = {{ {' '.join(f.get('filters', ['FOCUS_FILTER_POLITICAL']))} }}\n"
        s += f"\t\tai_will_do = {{\n\t\t\tfactor = {f.get('ai', 1)}\n\t\t}}\n"
        s += f"\t\tcompletion_reward = {{\n{f['reward']}\t\t}}\n"
        s += '\t}\n\n'
        loc(f['id'], f['name'])
        loc(f"{f['id']}_desc", f['desc'])
    return s.rstrip('\n') + '\n}\n'


T3 = '\t\t\t'
MIL = ['FOCUS_FILTER_MILITARY']

# Saladin's 1187 claims: Jerusalem, Oultrejordain, Tripoli, Antioch
LEVANT = [454, 455, 553, 799]

THIRD_CRUSADE = f'''{T3}every_country = {{
{T3}	limit = {{
{T3}		OR = {{ tag = AGV tag = FRK tag = HRE }}
{T3}		is_ai = yes
{T3}		is_in_faction = no
{T3}		NOT = {{ has_war_with = JRS }}
{T3}	}}
{T3}	JRS = {{ add_to_faction = PREV }}
{T3}	declare_war_on = {{ target = AYB type = annex_everything }}
{T3}	add_ideas = dv_crusader_vow
{T3}}}
{T3}add_war_support = 0.10
'''

JRS = [
    dict(id='dv_jrs_horns_of_hattin', name='The Horns of Hattin', icon='GFX_goal_generic_major_war', x=6, y=0, cost=3, filters=MIL,
         desc='The army of Jerusalem has marched out to meet Saladin. Whatever happens at Hattin, the kingdom must survive it.',
         reward=f'{T3}army_experience = 15\n{T3}add_war_support = 0.05\n'),
    # military branch
    dict(id='dv_jrs_defend_tyre', name='Hold Tyre', icon='GFX_goal_generic_fortify_city', x=2, y=1, pre=['dv_jrs_horns_of_hattin'], filters=MIL,
         desc='Conrad of Montferrat has arrived in Tyre. While Tyre holds, the kingdom lives.',
         reward=f'{T3}add_manpower = 5000\n{T3}553 = {{ add_building_construction = {{ type = infrastructure level = 1 instant_build = yes }} }}\n'),
    dict(id='dv_jrs_military_orders', name='The Military Orders', icon='GFX_goal_generic_special_forces', x=2, y=2, pre=['dv_jrs_defend_tyre'], filters=MIL,
         desc='Give the Templars and Hospitallers command of the frontier castles.',
         reward=f'{T3}add_ideas = dv_military_orders\n'),
    dict(id='dv_jrs_turcopoles', name='Raise the Turcopoles', icon='GFX_goal_generic_cavalry', x=1, y=3, pre=['dv_jrs_military_orders'], filters=MIL,
         desc='Recruit local horsemen who can match the Turkish horse archers.',
         reward=f'{T3}add_ideas = dv_turcopoles\n{T3}add_equipment_to_stockpile = {{ type = infantry_equipment_0 amount = 500 producer = JRS }}\n'),
    dict(id='dv_jrs_siege_engines', name='Engines of War', icon='GFX_goal_generic_army_artillery', x=3, y=3, pre=['dv_jrs_military_orders'], filters=MIL,
         desc='Build the mangonels and trebuchets we need to take back our cities.',
         reward=f'{T3}add_equipment_to_stockpile = {{ type = artillery_equipment_1 amount = 100 producer = JRS }}\n{T3}army_experience = 10\n'),
    dict(id='dv_jrs_reclaim_jerusalem', name='Reclaim Jerusalem', icon='GFX_goal_generic_occupy_states_ongoing_war', x=2, y=4,
         pre=['dv_jrs_turcopoles', 'dv_jrs_siege_engines'], filters=MIL,
         desc='The Holy City must be Christian again, whatever the cost.',
         reward=''.join(f'{T3}add_state_core = {s}\n' for s in LEVANT) + f'{T3}add_war_support = 0.10\n'),
    # diplomacy branch
    dict(id='dv_jrs_appeal_to_the_pope', name='Appeal to the Pope', icon='GFX_goal_generic_improve_relations', x=6, y=1, pre=['dv_jrs_horns_of_hattin'],
         desc='Send Archbishop Joscius west with the news. Christendom must answer.',
         reward=f'{T3}add_political_power = 75\n{T3}if = {{\n{T3}\tlimit = {{ country_exists = PPS }}\n{T3}\tadd_opinion_modifier = {{ target = PPS modifier = dv_same_faith }}\n{T3}}}\n'),
    dict(id='dv_jrs_the_third_crusade', name='The Third Crusade', icon='GFX_goal_generic_major_alliance', x=5, y=2, pre=['dv_jrs_appeal_to_the_pope'],
         mutex=['dv_jrs_peace_with_saladin'],
         available=f'{T3}has_war_with = AYB\n',
         desc='Richard of England, Philip of France and Frederick Barbarossa take the cross. Any of them still ruled by the AI joins our faction and marches on Saladin.',
         reward=THIRD_CRUSADE),
    dict(id='dv_jrs_peace_with_saladin', name='Peace with Saladin', icon='GFX_goal_generic_neutrality_focus', x=7, y=2, pre=['dv_jrs_appeal_to_the_pope'],
         mutex=['dv_jrs_the_third_crusade'],
         available=f'{T3}has_war_with = AYB\n',
         desc='Saladin is a man of his word. Make peace while the kingdom still has something left to save.',
         reward=f'{T3}white_peace = AYB\n{T3}add_stability = 0.10\n{T3}add_war_support = -0.10\n'),
    dict(id='dv_jrs_lionheart', name='The Lionheart Arrives', icon='GFX_goal_generic_amphibious_assault', x=5, y=3, pre=['dv_jrs_the_third_crusade'], filters=MIL,
         desc='The crusaders land at Acre. With Europe at our side, the war can be won.',
         reward=f'{T3}army_experience = 25\n{T3}add_manpower = 10000\n'),
    # internal branch
    dict(id='dv_jrs_haute_cour', name='Summon the High Court', icon='GFX_goal_generic_national_unity', x=10, y=1, pre=['dv_jrs_horns_of_hattin'],
         desc='The barons of the kingdom must stop quarrelling and stand behind the king.',
         reward=f'{T3}add_stability = 0.10\n{T3}add_political_power = 50\n'),
    dict(id='dv_jrs_italian_merchants', name='Italian Merchants', icon='GFX_goal_generic_trade', x=9, y=2, pre=['dv_jrs_haute_cour'],
         filters=['FOCUS_FILTER_INDUSTRY'],
         desc='Grant trading quarters to the Italian republics in return for ships and silver.',
         reward=f'{T3}add_ideas = dv_italian_merchants\n{T3}add_offsite_building = {{ type = arms_factory level = 1 }}\n'),
    dict(id='dv_jrs_castles', name='Rebuild the Castles', icon='GFX_goal_generic_construction', x=11, y=2, pre=['dv_jrs_haute_cour'],
         filters=['FOCUS_FILTER_INDUSTRY'],
         desc='Krak des Chevaliers, Margat and Kerak must be made ready for the next siege.',
         reward=f'{T3}random_owned_controlled_state = {{\n{T3}\tadd_building_construction = {{ type = infrastructure level = 1 instant_build = yes }}\n{T3}}}\n{T3}add_offsite_building = {{ type = industrial_complex level = 1 }}\n'),
    dict(id='dv_jrs_kingdom_endures', name='The Kingdom Endures', icon='GFX_goal_generic_defence', x=10, y=3, pre=['dv_jrs_italian_merchants', 'dv_jrs_castles'],
         desc='The Latin Kingdom of Jerusalem has survived its darkest hour.',
         reward=f'{T3}add_ideas = dv_kingdom_endures\n'),
]

AYB = [
    dict(id='dv_ayb_unite_the_faithful', name='Unite the Faithful', icon='GFX_goal_generic_national_unity', x=6, y=0, cost=3,
         desc='Egypt and Syria answer to one sultan for the first time in a century. Now they must fight as one.',
         reward=f'{T3}add_political_power = 50\n{T3}add_war_support = 0.05\n'),
    # military branch
    dict(id='dv_ayb_mamluks', name='Mamluk Regiments', icon='GFX_goal_generic_army_doctrines', x=2, y=1, pre=['dv_ayb_unite_the_faithful'], filters=MIL,
         desc='Expand the corps of slave-soldiers who form the core of the sultan\'s army.',
         reward=f'{T3}add_ideas = dv_mamluk_regiments\n'),
    dict(id='dv_ayb_victory_at_hattin', name='Victory at Hattin', icon='GFX_goal_generic_major_war', x=2, y=2, pre=['dv_ayb_mamluks'], filters=MIL,
         desc='The Frankish army lies broken on the Horns of Hattin. Their cities are defenceless.',
         reward=f'{T3}army_experience = 25\n{T3}add_war_support = 0.10\n'),
    dict(id='dv_ayb_take_jerusalem', name='Take Jerusalem', icon='GFX_goal_generic_occupy_states_ongoing_war', x=1, y=3, pre=['dv_ayb_victory_at_hattin'], filters=MIL,
         desc='Al-Quds must return to Islam, as it was before the Franks came.',
         reward=f'{T3}add_state_core = 454\n{T3}add_state_core = 455\n{T3}add_stability = 0.05\n'),
    dict(id='dv_ayb_sweep_the_coast', name='Sweep the Coast', icon='GFX_goal_generic_occupy_states_coastal', x=3, y=3, pre=['dv_ayb_victory_at_hattin'], filters=MIL,
         desc='Acre, Tyre, Tripoli and Antioch: take every port before help comes from the sea.',
         reward=f'{T3}add_state_core = 553\n{T3}add_state_core = 799\n{T3}add_equipment_to_stockpile = {{ type = artillery_equipment_1 amount = 100 producer = AYB }}\n'),
    dict(id='dv_ayb_saladin_in_the_field', name='Saladin Takes the Field', icon='GFX_goal_generic_position_armies', x=2, y=4,
         pre=['dv_ayb_take_jerusalem', 'dv_ayb_sweep_the_coast'], filters=MIL,
         desc='The sultan leads the army in person.',
         reward=f'{T3}create_field_marshal = {{\n{T3}\tname = "Saladin"\n{T3}\ttraits = {{ }}\n{T3}\tskill = 5\n{T3}\tattack_skill = 5\n{T3}\tdefense_skill = 4\n{T3}\tplanning_skill = 4\n{T3}\tlogistics_skill = 4\n{T3}}}\n'),
    # diplomacy branch
    dict(id='dv_ayb_caliphs_blessing', name="The Caliph's Blessing", icon='GFX_goal_generic_improve_relations', x=6, y=1, pre=['dv_ayb_unite_the_faithful'],
         desc='Seek the blessing of the Abbasid Caliph in Baghdad for the war against the Franks.',
         reward=f'{T3}add_political_power = 75\n{T3}if = {{\n{T3}\tlimit = {{ country_exists = ABS }}\n{T3}\tadd_opinion_modifier = {{ target = ABS modifier = dv_same_faith }}\n{T3}}}\n'),
    dict(id='dv_ayb_proclaim_jihad', name='Proclaim the Jihad', icon='GFX_goal_generic_major_alliance', x=5, y=2, pre=['dv_ayb_caliphs_blessing'],
         mutex=['dv_ayb_treaty_of_ramla'],
         available=f'{T3}has_war_with = JRS\n',
         desc='Call every Muslim ruler to the holy war. The Artuqids and the Caliph join our alliance if the AI rules them.',
         reward=f'''{T3}every_country = {{
{T3}	limit = {{
{T3}		OR = {{ tag = ARQ tag = ABS }}
{T3}		is_ai = yes
{T3}		is_in_faction = no
{T3}		NOT = {{ has_war_with = AYB }}
{T3}	}}
{T3}	AYB = {{ add_to_faction = PREV }}
{T3}	declare_war_on = {{ target = JRS type = annex_everything }}
{T3}	add_ideas = dv_jihad
{T3}}}
{T3}add_ideas = dv_jihad
'''),
    dict(id='dv_ayb_treaty_of_ramla', name='Treaty of Ramla', icon='GFX_goal_generic_neutrality_focus', x=7, y=2, pre=['dv_ayb_caliphs_blessing'],
         mutex=['dv_ayb_proclaim_jihad'],
         available=f'{T3}has_war_with = JRS\n',
         desc='Leave the Franks their coast and let the pilgrims come. The empire needs peace more than glory.',
         reward=f'{T3}white_peace = JRS\n{T3}add_stability = 0.15\n{T3}add_war_support = -0.10\n'),
    # internal branch
    dict(id='dv_ayb_egyptian_grain', name='Egyptian Grain', icon='GFX_goal_generic_consumer_goods', x=10, y=1, pre=['dv_ayb_unite_the_faithful'],
         filters=['FOCUS_FILTER_INDUSTRY'],
         desc='Organise the Nile harvest to feed the armies in Syria.',
         reward=f'{T3}add_ideas = dv_egyptian_grain\n'),
    dict(id='dv_ayb_citadel_of_cairo', name='The Citadel of Cairo', icon='GFX_goal_generic_fortify_city', x=9, y=2, pre=['dv_ayb_egyptian_grain'],
         filters=['FOCUS_FILTER_INDUSTRY'],
         desc='Build a fortress on the Muqattam hills to guard the capital.',
         reward=f'{T3}907 = {{ add_building_construction = {{ type = infrastructure level = 1 instant_build = yes }} }}\n{T3}add_offsite_building = {{ type = arms_factory level = 1 }}\n'),
    dict(id='dv_ayb_madrasas', name='Madrasas and Waqf', icon='GFX_goal_generic_scientific_exchange', x=11, y=2, pre=['dv_ayb_egyptian_grain'],
         filters=['FOCUS_FILTER_RESEARCH'],
         desc='Endow schools in Cairo, Damascus and Aleppo.',
         reward=f'{T3}add_ideas = dv_madrasas\n'),
    dict(id='dv_ayb_sultan_of_egypt_and_syria', name='Sultan of Egypt and Syria', icon='GFX_goal_generic_political_pressure', x=10, y=3,
         pre=['dv_ayb_citadel_of_cairo', 'dv_ayb_madrasas'],
         desc='No one in the Muslim world can now doubt who rules from the Nile to the Euphrates.',
         reward=f'{T3}add_ideas = dv_sultan_of_egypt_and_syria\n'),
]

w('common/national_focus/dv_jerusalem.txt', focus_tree('dv_jerusalem_focus', 'JRS', JRS))
w('common/national_focus/dv_ayyubid.txt', focus_tree('dv_ayyubid_focus', 'AYB', AYB))

w('localisation/english/dv_content_l_english.yml', 'l_english:\n' + '\n'.join(LOC) + '\n', bom=True)
print('wrote', len(LOC), 'localisation keys')
