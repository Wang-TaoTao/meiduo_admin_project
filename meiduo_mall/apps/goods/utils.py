def get_breadcrumb(category):

    breadcrumb = {
        'cat1':'',
        'cat2':'',
        'cat3':'',
    }

    if category.parent is None:
        #没有父级,说明是一级分类
        breadcrumb['cat1']=category
    elif category.subs.count() == 0:
        #没有子级,说明是三级分类
        breadcrumb['cat3']=category
        #二级
        breadcrumb['cat2']=category.parent
        #一级
        breadcrumb['cat1']=category.parent.parent

    else:
        #二级分类
        breadcrumb['cat2']=category
        breadcrumb['cat1']=category.parent

    return breadcrumb