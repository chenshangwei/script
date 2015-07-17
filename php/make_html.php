<?php
/*
* 一个简单的生成静态HTML的机制（OOP）
* @notice 代码未经过严格测试，请按实际情况修改相关代码
* 1.框架中实现，oop思想
* 2.支持内容分页
* 3.支持批量生成,js跳转
* 4.ob_start捕获整个页面
*/
class controller_post extends controller{
    private $page = 1;//当前页-> ！！内容分页使用
    private $id = 1;//文章id
    private $m_article = NULL;//文章model
    private $info = array();//指定文章信息
/*
* 构造方法,准备信息
* 成员属性记录信息
* 这些信息在预览 $this->view() 和生成 $this->make() 时被使用
*/
public function  __construct()
{
    //文章id $_GET传入 必须
    $this->id = (isset($_GET['id']) && $_GET['id']>0) ? intval($_GET['id']) : 1;
    $this->page = (isset($_GET['page']) && $_GET['page']>0) ? intval($_GET['page']) : 1;
    //获得某篇文章 的信息
    $this->m_article = model::factory('article');
    $this->info = $this->m_article->get_article_by_id($this->id);
}
/*
* 预览文章页
* @notice $this->page 对内容的影响
*/
public function view()
{
    $info = $this->info;
    //其他内容准备，如推荐，相关......
    $arr_body = preg_split('/#p#/',$info['body']);//将内容分割，以作分页
    $body = $arr_body[$this->page-1];//根 据$this->page值的不同，取对应的分页内容
    $this->view = view::factory('article');//文章模板
    //...............内容赋予模板
    $this->view->render();//内容输出
}
/*
* 生成静态页
* 生成指定文章的HTML页面,
*/
public function make()
{
    $id= $this->id;
    $info= $this->info;
    //$info['body'] 是文章内容,内容中可能有特殊标签，提示内容分页
    if(isset($info['body']) && !empty($info['body']))
    {
        $arr_body= preg_split('/#p#/',$info['body']);//将内容分割，以作分页
        $total= count($arr_body);
        for($i=1;$i<=$total;$i++)
        {
            /*
            * 从文章信息中，拼装生成页面所需要的参数
            * 以下just example
            */
            //////////////////////////////////////////
            $dir= '/data/wwwroot/news/2012/0316/';
            $name= '34.html';//分页时10000_$i.html
            $url= 'http://www.diy178.net/news/2012/0316/34.html';
            ///////////////////////////////////////////
            ob_start();
            $this->page = $i;//此处成员属性的变化，会影响到$this->view()时的页面内容
            $this->view();//内容输出，让ob_start()捕获
            $content = ob_get_contents();//这里就是你所预览的全部内容
            ob_end_clean();
            //写html
            $result = $this->make_html($dir,$name,$content);
            if($result== 1)
            {
                echo'成功生成：'.$url.'<a href="'.$url.'" target="_blank">点击查看</a>';
            }
            else
            {
                echo'生成失败：'.$url;
            }
        }
        return $result;
    }
    else
    {
        echo'<font color=red>没有内容，不生成页面！</font>';
        return 1;
    }
}
/*
* 批量生成静态页
* @param start 开始文章id
* @param end 结束文章id
*/
public function create()
{
    $start = isset($_GET['start']) ? (int)$_GET['start'] : 1;
    $end = isset($_GET['end']) ? (int)$_GET['end'] : 1;
    $this->id = isset($_GET['id']) ? (int)$_GET['id'] : $start;
    echo '正在生成文章静态页面,id范围为:<font color=red>'.$start.'~'.$end.'</font>，请不要离开或者关闭浏览器！<br />';
    echo '正在生成id为<font color=red>'.$this->id.'</font>的文章！<br />';
    if($this->make() == 1)
    {
        if($this->id < $end)
        {
            $next_id= $this->m_article->get_next_id($this->id);//下一篇文章的id
            echo"<script>window.location.href='http://www.ling01.com/post/create?id=".$next_id
                ."&start=".$start."&end=".$end."'</script>";
        }
        else
        {
            echo'<font color=red>创建完毕！可以离开</font><br />';
        }
    }
    else
    {
        echo'<font color=red>创建失败！请检查原因！</font><br />';exit();
    }
}
/*
* 生成单个HTML
* @dir 需要生成文件所在目录
* @name 文件名
* @content 文件的内容
* @return 1
* 0 -1
*/
private function make_html($dir,$name,$content='')
{
//检查要写入的目录
    if(!file_exists($dir))
    {
        //目录不存在，新建目录
        if(!mkdir($dir,0777,TRUE))
        {
            throw new Exception($dir.'目录创建不成功！请检查权限');
        }
    }
    $filename = $dir.$name;
    $f = fopen($filename, 'w+');
    if(fwrite($f, $content))
    {
        fclose($f);
        return 1;//生成成功
    }
    else
    {
        fclose($f);
        throw new Exception($filename.'文件创建不成功！请检查权限');
    }
}
