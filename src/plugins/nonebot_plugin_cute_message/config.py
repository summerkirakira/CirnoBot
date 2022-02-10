from pydantic import BaseSettings


class Config(BaseSettings):

    class Config:
        extra = "ignore"
        enabled_poke = []
        emoji = [
            '(๑>◡<๑) ',
            '( /) V (\\ ) ',
            '(❁´▽`❁)',
            '(≧▽≦)',
            ' (´・ω・｀)',
            'ヽ( ^∀^)ﾉ',
            '(́>◞౪◟<‵)ﾉｼ',
            '(́つ◞౪◟⊂‵)',
            '( >﹏<。)～'
        ]
        message_after_poke = [
            '再戳，再戳，就把你吃掉！',
            '戳了我，你就是下个AI啦～',
            '嗷呜～',
            '再戳，请你吃冻青蛙！',
            '汪汪汪！',
            'あたいってば最強ね！',
            'あ～た～い！',
            '欸～有什么事嘛～',
            '你们这群笨蛋！',
            '戳戳戳～',
            '戳戳～',
            '别以为人家会搭理你哦！',
            '诶嘿嘿～',
            '让人家帮忙的话「.帮助」就行啦～',
            '戳戳戳戳～',
            '喵喵喵？',
            '喵！',
            '再戳也不会理你的哦！',
            '再戳再戳再戳！',
            '抱抱～',
            '抱住胳膊就是一口！'
        ]
        basic_response_dict = {
            '早[早上安好呀]': [
                {
                    'text': '不要说早，要说我爱你～',
                    'image': 'BE6A82E08F745FCFD7304A3C9491701A.jpg'
                },
                {
                    'text': '',
                    'image': '416c57755805ba7a.jpg'
                },
                {
                    'text': '',
                    'image': ''
                },
                {
                    'text': '早早早，确定不睡个回笼觉么？',
                    'image': '4837479E7EC3C7DDB4C9953CA4AC8B5E.jpg'
                },
                {
                    'text': '早',
                    'image': '-58e3fd36b5ef274a.jpg'
                },
                {
                    'text': '早上好呀，懒狗。',
                    'image': '1626849431260.png'
                },
                {
                    'text': '看看都几点了啦！',
                    'image': '-58e3fd36b5ef274a.jpg'
                },
                {
                    'text': '起床了啦！',
                    'image': '7f933bbc5c3bd039.jpg'
                },
                {
                    'text': '唔...早上好？',
                    'image': '39D0C44BC2A0D3727F42F97E6BEDCBA6.jpg'
                }
            ],
            '小九抱抱.*': [
                {
                    'text': '不准抱！你抱得动吗！？',
                    'image': ''
                },
                {
                    'text': 'ばか、変態、煩い！',
                    'image': '898FD56084D82F603239BBFC92516817.jpg'
                },
            ],
            '.*举高高.*': {
                'text': '不准举！你举得动吗！？',
                'image': 'dcf07a381f30e9240bf68c845b086e061c95f72a.jpg'
            },
            # '^小九.?': [
            #     {
            #         'text': '以为这样咱就会理你了吗？想太美了！',
            #         'image': 'b9b6a819ebc4b745e7b5f77ed8fc1e178b82159c.jpg'
            #     },
            #     {
            #         'text': '叫咱就为这点事呀～',
            #         'image': 'bcc759a7d933c89589fe032bc61373f0800200c5.jpg'
            #     },
            #     {
            #         'text': '呀呀呀～吃我一拳！',
            #         'image': '2db214b30f2442a7b14354cac643ad4bd0130277.jpg'
            #     },
            #     {
            #         'text': '煩い！',
            #         'image': '473867A7FD46FD3063EC72D1B4CAC046.jpg'
            #     },
            #     {
            #         'text': '',
            #         'image': 'C2B902C72FF90997EAF73761FD41D2C6.jpg'
            #     },
            #     {
            #         'text': '',
            #         'image': '2db214b30f2442a7b14354cac643ad4bd0130277.jpg'
            #     }
            # ],
            '.*我爱你.*': [
                {
                    'text': '',
                    'image': '-4d0461074e6aa354.jpg'
                }
            ],
            '^[查\-]': [
                {
                    'text': '请小伙伴使用「.」哦 Σ( ° △ °|||)',
                    'image': 'b9b6a819ebc4b745e7b5f77ed8fc1e178b82159c.jpg'
                },
                {
                    'text': '这...这是什么？小九不认识呢...请使用「.」的说',
                    'image': '-58e3fd36b5ef274a.jpg'
                },
                {
                    'text': '过分！！！请使用「.」',
                    'image': 'B8427C41146B46AA6A750C12160FE54D.jpg'
                },
                {
                    'text': '不要使用一些奇怪的符号啦o(≧口≦)o 请使用「.」',
                    'image': '2db214b30f2442a7b14354cac643ad4bd0130277.jpg'
                },
                {
                    'text': '尊重咱的工作啦QAQ 请使用「.」',
                    'image': '7606F8F9C39E798A7E448936F25EED7D.jpg'
                }
            ],
            '.*色图.*': [
                {
                    'text': '',
                    'image': '520e3ff8dd22a9de.png'
                },
                {
                    'text': '',
                    'image': '167777936156F66741FEC6200886757C.jpg'
                },
                {
                    'text': '',
                    'image': '54a6f0c8a786c917417f582a943d70cf3bc75715.jpg'
                },
                {
                    'text': '诶嘿嘿～不存在的哦～',
                    'image': ''
                },
                {
                    'text': '是瑟瑟！',
                    'image': 'FCA369BABFC7ACFC02468832E4BC093C.jpg'
                }
            ],
            '恰小九.?': [
                {
                    'text': '咱 咱不能吃哦？',
                    'image': '3c736034970a304efdad73b6c6c8a786c8175c58'
                },
                {
                    'text': '咱 咱不好吃哦？？',
                    'image': '3c736034970a304efdad73b6c6c8a786c8175c58'
                }
            ],
            '.{0,2}晚安.?': [
                {
                    'text': '熬..熬夜是坏文明...',
                    'image': '61aed9007d011d66.jpg'
                },
                {
                    'text': '睡觉觉～',
                    'image': 'fd17eea477629f1.jpg'
                },
                {
                    'text': '',
                    'image': ''
                }
            ]
        }
